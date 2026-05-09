import json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
reg = json.loads((root/'registries'/'transport_adapters.json').read_text(encoding='utf-8'))
adapters = reg.get('adapters', reg) if isinstance(reg, dict) else reg
ids = {a['adapter_id'] for a in adapters}
required = {'local_loopback','meshtastic_serial','reticulum_rns','reticulum_lxmf','lan_http','bluetooth_ble','storage_node','phone_cache','drone_mule'}
missing = sorted(required - ids)
body = '# Transport Skeleton Report\n\n'
body += 'PASS\n' if not missing else 'FAIL missing: ' + ', '.join(missing) + '\n'
(root/'audit_reports'/'active'/'transport_skeleton_report.md').write_text(body, encoding='utf-8')
print('TRANSPORT_SKELETON_' + ('PASS' if not missing else 'FAIL'))
raise SystemExit(1 if missing else 0)
