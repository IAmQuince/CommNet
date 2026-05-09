from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _public_id(seed: str) -> str:
    digest = hashlib.sha256(seed.encode('utf-8')).hexdigest().upper()
    # Avoid ambiguous characters where practical.
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    out = []
    for i in range(0, 24, 2):
        out.append(alphabet[int(digest[i:i+2], 16) % len(alphabet)])
    return 'CommNet_' + ''.join(out[:8])


def ensure_node_identity(cfg: dict[str, Any]) -> dict[str, Any]:
    changed = False
    if not cfg.get('node_id'):
        cfg['node_id'] = 'node_' + uuid.uuid4().hex
        changed = True
    if not cfg.get('commnet_user_id'):
        cfg['commnet_user_id'] = _public_id(str(cfg['node_id']))
        changed = True
    if not cfg.get('node_display_name'):
        cfg['node_display_name'] = cfg.get('node_name') or 'Local CommNet Node'
        changed = True
    if not cfg.get('identity_created_at'):
        cfg['identity_created_at'] = _now()
        changed = True
    cfg['_identity_changed'] = changed
    return cfg


def identity_summary(cfg: dict[str, Any]) -> dict[str, Any]:
    return {
        'node_id': cfg.get('node_id'),
        'commnet_user_id': cfg.get('commnet_user_id'),
        'node_display_name': cfg.get('node_display_name') or cfg.get('node_name'),
        'visibility_mode': cfg.get('visibility_mode'),
    }
