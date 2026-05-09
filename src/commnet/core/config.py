from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from commnet.core.config_schema import DEFAULT_CONFIG
from commnet.core.config_validation import validate_config


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


class ConfigManager:
    def __init__(self, paths):
        self.paths = paths
        self.path = paths.config / 'current_config.json'
        self.snapshots = paths.config / 'snapshots'
        self.index_path = self.snapshots / 'snapshot_index.json'

    def ensure_default(self) -> dict[str, Any]:
        self.paths.ensure_all()
        self.snapshots.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            cfg = json.loads(json.dumps(DEFAULT_CONFIG))
            now = _now()
            cfg['created_at'] = now
            cfg['last_started_at'] = now
            cfg['updated_at'] = now
            self.save(cfg, snapshot=False, reason='create_default')
        else:
            cfg = self.load()
            merged = self._merge_defaults(cfg)
            if merged != cfg:
                self.save(merged, snapshot=True, reason='merge_default_config_schema')
        return self.load()

    def _merge_defaults(self, cfg: dict[str, Any]) -> dict[str, Any]:
        def merge(default, current):
            if isinstance(default, dict):
                out = dict(default)
                if isinstance(current, dict):
                    for k, v in current.items():
                        out[k] = merge(default.get(k), v) if k in default else v
                return out
            return current if current is not None else default
        merged = merge(DEFAULT_CONFIG, cfg)
        if 'created_at' not in merged:
            merged['created_at'] = _now()
        return merged

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return self.ensure_default()
        return json.loads(self.path.read_text(encoding='utf-8'))

    def validate(self, cfg: dict[str, Any]) -> list[str]:
        return validate_config(cfg)

    def save(self, cfg: dict[str, Any], snapshot: bool = True, reason: str = 'config_update') -> dict[str, Any]:
        self.paths.ensure_all()
        self.snapshots.mkdir(parents=True, exist_ok=True)
        cfg = self._merge_defaults(cfg)
        cfg['updated_at'] = _now()
        errors = self.validate(cfg)
        if errors:
            raise ValueError('; '.join(errors))
        self.path.write_text(json.dumps(cfg, indent=2, sort_keys=True), encoding='utf-8')
        if snapshot:
            self.snapshot(reason=reason, cfg=cfg)
        return cfg

    def snapshot(self, reason: str = 'manual_snapshot', cfg: dict[str, Any] | None = None) -> dict[str, Any]:
        self.paths.ensure_all()
        self.snapshots.mkdir(parents=True, exist_ok=True)
        cfg = cfg if cfg is not None else self.load()
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        digest = stable_hash(cfg)
        filename = f'config_{ts}_{digest[:10]}.json'
        path = self.snapshots / filename
        path.write_text(json.dumps(cfg, indent=2, sort_keys=True), encoding='utf-8')
        item = {'created_at': _now(), 'reason': reason, 'filename': filename, 'config_hash': digest}
        index = self.snapshot_index()
        index.append(item)
        self.index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding='utf-8')
        return item

    def snapshot_index(self) -> list[dict[str, Any]]:
        if not self.index_path.exists():
            return []
        try:
            return json.loads(self.index_path.read_text(encoding='utf-8'))
        except Exception:
            return []

    def restore_snapshot(self, filename: str) -> dict[str, Any]:
        if '/' in filename or '\\' in filename or '..' in filename:
            raise ValueError('Unsafe snapshot filename.')
        path = self.snapshots / filename
        if not path.exists():
            raise FileNotFoundError(filename)
        cfg = json.loads(path.read_text(encoding='utf-8'))
        self.save(cfg, snapshot=True, reason=f'restore_snapshot:{filename}')
        return cfg

    def export_config_text(self) -> str:
        return json.dumps(self.load(), indent=2, sort_keys=True)

    def import_config_text(self, text: str) -> dict[str, Any]:
        cfg = json.loads(text)
        if not isinstance(cfg, dict):
            raise ValueError('Imported config must be a JSON object.')
        return self.save(cfg, snapshot=True, reason='import_config')

    def reset_safe_defaults(self) -> dict[str, Any]:
        cfg = json.loads(json.dumps(DEFAULT_CONFIG))
        now = _now()
        cfg['created_at'] = now
        cfg['last_started_at'] = now
        cfg['updated_at'] = now
        return self.save(cfg, snapshot=True, reason='reset_safe_defaults')

    def touch_started(self) -> dict[str, Any]:
        cfg = self.ensure_default()
        cfg['last_started_at'] = _now()
        self.save(cfg, snapshot=False, reason='server_start_touch')
        return cfg

    def redact(self, cfg: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.loads(json.dumps(cfg if cfg is not None else self.load()))
        # Reserved for future sensitive fields.
        for key in ['tokens', 'secrets', 'passwords']:
            if key in data:
                data[key] = '[REDACTED]'
        return data
