from __future__ import annotations
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
prev_marker = root / 'proof' / 'previous_active_docs.txt'
current = sorted(p.name for p in (root/'docs'/'active').glob('*.md'))
previous = [line.strip() for line in prev_marker.read_text(encoding='utf-8').splitlines() if line.strip()]
missing = sorted(set(previous) - set(current))
added = sorted(set(current) - set(previous))
lines = ['# Documentation Retention Report','', f'Previous active docs: `{len(previous)}`', f'Current active docs: `{len(current)}`', f'Missing previous docs: `{len(missing)}`', f'Added docs: `{len(added)}`','']
if missing:
    lines += ['## Missing prior docs'] + [f'- `{x}`' for x in missing]
else:
    lines += ['## Missing prior docs','- None']
lines += ['', '## Added docs'] + ([f'- `{x}`' for x in added] if added else ['- None'])
(root/'audit_reports'/'active'/'doc_retention_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print('DOC_RETENTION_' + ('PASS' if not missing else 'FAIL'))
sys.exit(0 if not missing else 1)
