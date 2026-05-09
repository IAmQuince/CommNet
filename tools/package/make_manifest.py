import hashlib, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
items = []
for p in sorted(root.rglob('*')):
    if p.is_file() and '.zip' not in p.name:
        rel = str(p.relative_to(root)).replace('\\','/')
        items.append({'path': rel, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'size': p.stat().st_size})
out = root/'proof'/'manifest.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({'package': root.name, 'files': items}, indent=2), encoding='utf-8')
print(out)
