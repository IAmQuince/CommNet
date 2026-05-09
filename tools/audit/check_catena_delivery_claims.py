from __future__ import annotations
from pathlib import Path
root=Path(__file__).resolve().parents[2]
texts=[]
for p in list((root/'docs'/'active').glob('*Catena*.md')) + [root/'README.md', root/'RUN_STATUS.md']:
    texts.append(p.read_text(encoding='utf-8', errors='ignore'))
combined='\n'.join(texts).lower()
bad=['catena is meshtastic','ack proves remote','ack means remote','rf delivered by ack']
found=[b for b in bad if b in combined]
report=root/'audit_reports'/'active'/'catena_delivery_claims_report.md'
report.write_text('# Catena Delivery Claims Report\n\nFound bad claims: '+repr(found)+'\n\nResult: '+('PASS' if not found else 'FAIL')+'\n', encoding='utf-8')
raise SystemExit(0 if not found else 1)
