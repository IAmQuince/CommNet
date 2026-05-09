from __future__ import annotations
import json, sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
reg = json.loads((root/'registries'/'config_schema.json').read_text(encoding='utf-8'))
required = {'node_name','deployment_profile','privacy_mode','visibility_mode','desired_transport_profiles','services'}
fields = set(reg.get('fields', []))
missing = sorted(required - fields)
body = '# Config Schema Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: ' + ', '.join(missing) + '\n')
(root/'audit_reports'/'active'/'config_schema_report.md').write_text(body, encoding='utf-8')
print('CONFIG_SCHEMA_' + ('PASS' if not missing else 'FAIL'))
sys.exit(0 if not missing else 1)
