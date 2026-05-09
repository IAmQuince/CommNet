from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[2]
data=json.loads((root/'registries/peer_schema.json').read_text())
missing=set(['peer_id','display_name','base_url','trust_state'])-set(data.get('required',[]))
report=root/'audit_reports/active/peer_schema_report.md'; report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# Peer Schema Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: '+', '.join(missing)+'\n'), encoding='utf-8')
if missing: sys.exit(1)
print('PEER_SCHEMA_PASS')
