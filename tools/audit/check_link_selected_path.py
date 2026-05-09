from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from commnet.links.link_builder import build_base_urls
root=Path(__file__).resolve().parents[2]
report=root/'audit_reports'/'active'/'link_selected_path_report.md'
urls=build_base_urls([{'address':'169.254.143.75'},{'address':'192.168.1.225'}],8765)
ok=all('169.254.' not in u for u in urls) and urls[0].startswith('http://192.168.1.225')
report.write_text(f"# Link Selected Path Report\n\nURLs: {urls}\n\nResult: {'PASS' if ok else 'FAIL'}\n", encoding='utf-8')
raise SystemExit(0 if ok else 1)
