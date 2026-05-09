from pathlib import Path
root = Path(__file__).resolve().parents[2]
lines = [root.name + '/']
for p in sorted(root.rglob('*')):
    rel = p.relative_to(root)
    if any(part in {'__pycache__'} for part in rel.parts):
        continue
    depth = len(rel.parts)
    suffix = '/' if p.is_dir() else ''
    lines.append('  ' * depth + rel.name + suffix)
out = root/'proof'/'tree_report.txt'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(out)
