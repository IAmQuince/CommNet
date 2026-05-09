from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from commnet.network.path_selector import classify_path, best_network_path
root=Path(__file__).resolve().parents[2]
report=root/'proof'/'network_path_smoke_report.md'
paths=[
 {'path_id':'bad','adapter_name':'Ethernet 3','ipv4_address':'169.254.143.75','gateway':'','classification':'invalid','recommendation_score':-60,'suggested_url':''},
 {'path_id':'good','adapter_name':'Wi-Fi','ipv4_address':'192.168.1.225','gateway':'192.168.1.1','classification':'recommended','recommendation_score':100,'suggested_url':'http://192.168.1.225:8765/'}]
ok = classify_path('x','169.254.1.1')[0]=='invalid' and best_network_path(paths)['path_id']=='good'
report.write_text(f"# Network Path Smoke\n\nResult: {'PASS' if ok else 'FAIL'}\n", encoding='utf-8')
raise SystemExit(0 if ok else 1)
