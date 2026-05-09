import os
from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[2]
classes=set(json.loads((root/'registries/payload_classes.json').read_text()))
policy=json.loads((root/'registries/route_policy.json').read_text())
missing=sorted(classes-set(policy.keys()))
report=root/'audit_reports/active/message_class_report.md'; report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# Message Class Report\n\n' + ('PASS\n' if not missing else 'FAIL missing route policy: '+', '.join(missing)+'\n'), encoding='utf-8')
if missing: sys.exit(1)
print('MESSAGE_CLASS_PASS', flush=True)
os._exit(0)
