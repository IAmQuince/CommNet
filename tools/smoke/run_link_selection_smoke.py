from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from commnet.links.link_builder import build_base_urls
root=Path(__file__).resolve().parents[2]
urls=build_base_urls([{'address':'169.254.143.75'},{'address':'192.168.1.225'}],8765)
ok=urls==['http://192.168.1.225:8765']
(root/'proof'/'link_selection_smoke_report.md').write_text(f"# Link Selection Smoke\n\nURLs: {urls}\nResult: {'PASS' if ok else 'FAIL'}\n", encoding='utf-8')
raise SystemExit(0 if ok else 1)
