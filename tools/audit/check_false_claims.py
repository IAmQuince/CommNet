from pathlib import Path
root = Path(__file__).resolve().parents[2]
needles = ['Meshtastic hardware messaging', 'Reticulum/RNS or LXMF messaging', 'Bluetooth messaging']
text = (root/'README.md').read_text(encoding='utf-8') + '\n' + (root/'KNOWN_LIMITS.md').read_text(encoding='utf-8') + '\n' + (root/'RUN_STATUS.md').read_text(encoding='utf-8')
missing = [n for n in needles if n not in text]
body = '# False Claims Report\n\n' + ('PASS\n' if not missing else 'FAIL missing unfinished disclaimers: ' + ', '.join(missing) + '\n')
(root/'audit_reports'/'active'/'false_claims_report.md').write_text(body, encoding='utf-8')
print('FALSE_CLAIMS_' + ('PASS' if not missing else 'FAIL'))
raise SystemExit(0 if not missing else 1)
