from __future__ import annotations

import json
import platform
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from commnet.core.config import ConfigManager
from commnet.core.db import SQLiteStore
from commnet.core.peer_store import PeerStore
from commnet.transport.dependencies import check_all_dependencies
from commnet.transport.registry import build_default_registry
from commnet.share.store import ShareStore


class SupportBundle:
    def __init__(self, package_root: Path, paths):
        self.package_root = Path(package_root)
        self.paths = paths

    def create(self) -> Path:
        self.paths.ensure_all()
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        bundle_path = self.paths.support / f'commnet_support_{ts}.zip'
        cfg_mgr = ConfigManager(self.paths)
        store = SQLiteStore(self.paths); store.initialize()
        peers = PeerStore(store)
        deps = check_all_dependencies(store)
        adapters = build_default_registry(peers).statuses()
        share_store = ShareStore(store, None, self.package_root)
        share_summary = share_store.summary()
        summary = {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'python': sys.version,
            'platform': platform.platform(),
            'package_root': str(self.package_root),
            'current_config_redacted': cfg_mgr.redact(),
            'config_snapshot_count': len(cfg_mgr.snapshot_index()),
            'device_count': len(store.list_devices()),
            'file_root_count': len(store.list_file_roots()),
            'peer_count': len(peers.list()),
            'message_count': store.table_counts().get('messages', 0),
            'dependency_status': deps,
            'transport_status': adapters,
            'table_counts': store.table_counts(),
            'share_summary': share_summary,
        }
        summary_path = self.paths.reports / 'support_summary.json'
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'current_config_redacted.json').write_text(json.dumps(cfg_mgr.redact(), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'config_snapshot_index.json').write_text(json.dumps(cfg_mgr.snapshot_index(), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'device_registry_summary.json').write_text(json.dumps(store.list_devices(), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'file_roots_summary.json').write_text(json.dumps(store.list_file_roots(), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'peer_registry_summary.json').write_text(json.dumps(peers.list(), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'dependency_status.json').write_text(json.dumps(deps, indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'transport_status.json').write_text(json.dumps(adapters, indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'message_queue_summary.json').write_text(json.dumps(store.messages_recent(50), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'delivery_attempt_recent.json').write_text(json.dumps(store.delivery_attempts_recent(50), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'route_decision_recent.json').write_text(json.dumps(store.route_decisions_recent(50), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'share_summary.json').write_text(json.dumps(share_summary, indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'share_permissions_summary.json').write_text(json.dumps({'profiles': ['private','list_only','list_and_download','dropbox_upload_only','list_download_upload_inbox','advanced_custom']}, indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'lan_access_summary.json').write_text(json.dumps({'lan_access_enabled': cfg_mgr.load().get('lan_access_enabled'), 'lan_access_mode': cfg_mgr.load().get('lan_access_mode')}, indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'quick_setup_summary.json').write_text(json.dumps({'quick_setup_complete': cfg_mgr.load().get('quick_setup_complete')}, indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'share_access_recent.json').write_text(json.dumps(share_store.recent_access(50), indent=2, sort_keys=True), encoding='utf-8')
        (self.paths.reports / 'security_posture.md').write_text('# CommNet Security Posture\n\n' + json.dumps({'lan_access': cfg_mgr.load().get('lan_access_enabled'), 'shares': share_summary}, indent=2), encoding='utf-8')
        (self.paths.reports / 'network_summary.md').write_text('# CommNet Network Summary\n\n' + json.dumps({'peers': len(peers.list()), 'messages': store.table_counts().get('messages',0), 'dependencies': deps}, indent=2), encoding='utf-8')
        with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for base in [self.paths.logs, self.paths.reports, self.package_root / 'audit_reports' / 'active', self.package_root / 'proof']:
                if not base.exists():
                    continue
                for path in base.rglob('*'):
                    if path.is_file():
                        try:
                            arc = path.relative_to(self.package_root)
                        except ValueError:
                            arc = Path('runtime_support') / path.name
                        zf.write(path, arcname=str(arc).replace('\\', '/'))
            # Include snapshot index but not arbitrary user files or runtime cache.
        with store.connect() as conn:
            conn.execute('INSERT INTO support_exports(path, details_json) VALUES (?, ?)', (str(bundle_path), json.dumps({'redacted': True})))
            conn.commit()
        return bundle_path
