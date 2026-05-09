from pathlib import Path
import sys, os, re
root=Path(__file__).resolve().parents[2]
viol=[]
patterns=[r'production[- ]grade security', r'actual Meshtastic radio send', r'Reticulum works', r'Bluetooth works', r'fully working mesh']
for p in [root/'README.md', root/'RUN_STATUS.md', root/'KNOWN_LIMITS.md']:
    txt=p.read_text(errors='ignore') if p.exists() else ''
    for pat in patterns:
        if re.search(pat, txt, flags=re.I): viol.append(f'{p.name}: {pat}')
report=root/'audit_reports/active/network_false_claims_report.md'; report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# Network False Claims Report\n\n' + ('PASS\n' if not viol else 'FAIL\n'+'\n'.join('- '+v for v in viol)), encoding='utf-8')
if viol: sys.exit(1)
print('NETWORK_FALSE_CLAIMS_PASS', flush=True)
os._exit(0)
