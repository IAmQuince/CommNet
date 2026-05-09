from pathlib import Path
root = Path(__file__).resolve().parents[2]
long = []
for p in root.rglob('*'):
    rel = str(p.relative_to(root))
    if len(str(p)) > 180 or len(rel) > 160:
        long.append((len(str(p)), rel))
out = root / 'audit_reports' / 'active' / 'path_report.md'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('# Path Report\n\n' + ('PASS\n' if not long else 'WARN\n' + '\n'.join(f'- {n}: {r}' for n,r in long)), encoding='utf-8')
print('PATH_CHECK_' + ('PASS' if not long else 'WARN'))
