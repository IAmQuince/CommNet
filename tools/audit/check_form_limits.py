from __future__ import annotations
import json, sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
data = json.loads((root/'registries'/'form_limits.json').read_text(encoding='utf-8'))
limits = data.get('limits', {})
required = {'node_name','admin_display_name','node_description','file_root_path'}
missing = sorted(required - set(limits))
body = '# Form Limits Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: ' + ', '.join(missing) + '\n')
(root/'audit_reports'/'active'/'form_limits_report.md').write_text(body, encoding='utf-8')
print('FORM_LIMITS_' + ('PASS' if not missing else 'FAIL'))
sys.exit(0 if not missing else 1)
