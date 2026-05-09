from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from commnet.core.config import ConfigManager
from commnet.core.config_validation import validate_config
from commnet.core.db import SQLiteStore
from commnet.core.peer_store import PeerStore
from commnet.transport.dependencies import check_all_dependencies
from commnet.transport.registry import build_default_registry
from commnet.share.store import ShareStore
from commnet.setup.quick_setup import detect_all


class DiagnosticsRunner:
    def __init__(self, package_root: Path, paths):
        self.package_root = Path(package_root)
        self.paths = paths

    def run(self, write_reports: bool = True) -> dict:
        self.paths.ensure_all()
        cfg_mgr = ConfigManager(self.paths)
        cfg = cfg_mgr.ensure_default()
        store = SQLiteStore(self.paths)
        store.initialize()
        peers = PeerStore(store)
        registry = build_default_registry(peers)
        statuses = [a.probe().to_dict() for a in registry.adapters]
        share_store = ShareStore(store, None, self.package_root)
        share_summary = share_store.summary()
        validation_errors = validate_config(cfg)
        result = {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'overall_status': 'PASS' if not validation_errors else 'WARN',
            'package_root': str(self.package_root),
            'python_version': sys.version,
            'platform': platform.platform(),
            'runtime_root': str(self.paths.local),
            'config': cfg_mgr.redact(cfg),
            'config_validation': {'valid': not validation_errors, 'errors': validation_errors},
            'config_snapshot_count': len(cfg_mgr.snapshot_index()),
            'file_root_count': len(store.list_file_roots()),
            'device_count': len(store.list_devices()),
            'enabled_services': [k for k, v in (cfg.get('services') or {}).items() if v.get('enabled')],
            'desired_transport_profiles': cfg.get('desired_transport_profiles', []),
            'sqlite_path': str(store.path),
            'sqlite_integrity': store.integrity_check(),
            'table_counts': store.table_counts(),
            'transport_adapters': statuses,
            'dependencies': check_all_dependencies(store),
            'peers': peers.list(),
            'message_queue_depth': store.table_counts().get('messages', 0),
            'recent_delivery_attempts': store.delivery_attempts_recent(10),
            'recent_route_decisions': store.route_decisions_recent(10),
            'share_summary': share_summary,
            'quick_setup_detection': detect_all(),
            'limits': {
                'ui_dependency_policy': 'stdlib_core_with_optional_lazy_transport_dependencies',
                'server_bind_default': f"{cfg.get('lan_bind_host', cfg.get('server_host'))}:{cfg.get('lan_bind_port', cfg.get('server_port'))}",
                'inbound_peer_messages': cfg.get('allow_inbound_peer_messages', False),
            },
        }
        if result['sqlite_integrity'] != 'ok':
            result['overall_status'] = 'FAIL'
        if write_reports:
            self._write_reports(result)
        return result

    def _write_reports(self, result: dict) -> None:
        self.paths.reports.mkdir(parents=True, exist_ok=True)
        (self.paths.reports / 'diagnostic_report.json').write_text(json.dumps(result, indent=2, sort_keys=True), encoding='utf-8')
        lines = [
            '# CommNet Diagnostic Report', '',
            f"Status: `{result['overall_status']}`",
            f"Created: `{result['created_at']}`",
            f"Python: `{result['python_version'].split()[0]}`",
            f"Platform: `{result['platform']}`",
            f"SQLite integrity: `{result['sqlite_integrity']}`", '',
            '## Configuration', '',
            f"- Node: `{result['config'].get('node_name')}`",
            f"- Deployment: `{result['config'].get('deployment_profile')}`",
            f"- Visibility: `{result['config'].get('visibility_mode')}`",
            f"- Enabled services: {', '.join(result['enabled_services']) or 'none'}",
            f"- Device count: `{result['device_count']}`",
            f"- File root count: `{result['file_root_count']}`",
            f"- Snapshot count: `{result['config_snapshot_count']}`",
            f"- Peer count: `{len(result['peers'])}`",
            f"- Message count: `{result['message_queue_depth']}`",
            f"- Enabled shares: `{result['share_summary']['enabled_share_count']}`",
            f"- LAN-visible shares: `{result['share_summary']['lan_visible_share_count']}`",
            f"- Inbound peer messages: `{result['limits']['inbound_peer_messages']}`", '',
            '## Config validation', '',
            '- Valid: `' + str(result['config_validation']['valid']) + '`',
        ]
        if result['config_validation']['errors']:
            lines += [f"- {e}" for e in result['config_validation']['errors']]
        else:
            lines.append('- No validation errors.')
        lines += ['', '## Optional dependencies', '', '| Package | Import | Installed | Version | Profile |', '|---|---|---:|---|---|']
        for dep in result['dependencies']:
            lines.append(f"| {dep['package_name']} | {dep['import_name']} | {dep['installed']} | {dep.get('version') or ''} | {dep.get('profile','')} |")
        lines += ['', '## Transport adapters', '', '| Adapter | State | Installed | Available | Notes |', '|---|---:|---:|---:|---|']
        for item in result['transport_adapters']:
            lines.append(f"| {item['display_name']} | {item['state']} | {item['installed']} | {item['available']} | {item.get('notes','')} |")
        lines.append('')
        lines.append('## Share / LAN Access')
        lines.append('')
        lines.append(f"- LAN access enabled: `{result['config'].get('lan_access_enabled')}`")
        lines.append(f"- LAN access mode: `{result['config'].get('lan_access_mode')}`")
        lines.append(f"- Enabled shares: `{result['share_summary']['enabled_share_count']}`")
        lines.append(f"- Access codes active: `{result['share_summary']['access_code_count']}`")
        lines.append('')
        lines.append('## Network')
        lines.append('')
        lines.append(f"- Peers: `{len(result['peers'])}`")
        lines.append(f"- Messages: `{result['message_queue_depth']}`")
        lines.append(f"- Recent delivery attempts: `{len(result['recent_delivery_attempts'])}`")
        lines.append('')
        lines.append('## Database table counts')
        lines.append('')
        for k, v in result['table_counts'].items():
            lines.append(f'- `{k}`: {v}')
        (self.paths.reports / 'diagnostic_report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
