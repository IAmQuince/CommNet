from __future__ import annotations
import json, sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
data = json.loads((root/'registries'/'visibility_modes.json').read_text(encoding='utf-8'))
modes = set(data.get('visibility_modes', []))
required = {'private_local_only','visible_to_local_lan','visible_to_approved_peers','visible_to_community_directory','gateway_exposed'}
missing = sorted(required - modes)
body = '# Visibility Modes Report\n\n' + ('PASS\n' if not missing and data.get('default') == 'private_local_only' else 'FAIL\n')
if missing: body += 'Missing: ' + ', '.join(missing) + '\n'
(root/'audit_reports'/'active'/'visibility_modes_report.md').write_text(body, encoding='utf-8')
print('VISIBILITY_MODES_' + ('PASS' if not missing and data.get('default') == 'private_local_only' else 'FAIL'))
sys.exit(0 if not missing and data.get('default') == 'private_local_only' else 1)
