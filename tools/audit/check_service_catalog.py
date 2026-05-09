from __future__ import annotations
import json, sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
data = json.loads((root/'registries'/'service_defaults.json').read_text(encoding='utf-8'))
services = data.get('services', {})
required = {'community_portal','directory','emergency','bbs','retroweb','marketplace'}
missing = sorted(required - set(services))
body = '# Service Catalog Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: ' + ', '.join(missing) + '\n')
(root/'audit_reports'/'active'/'service_visibility_report.md').write_text(body, encoding='utf-8')
print('SERVICE_CATALOG_' + ('PASS' if not missing else 'FAIL'))
sys.exit(0 if not missing else 1)
