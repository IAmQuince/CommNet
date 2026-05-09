from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from commnet.network.path_selector import classify_path

root = Path(__file__).resolve().parents[2]
report = root / 'audit_reports' / 'active' / 'network_path_rules_report.md'
report.parent.mkdir(parents=True, exist_ok=True)
cls, score, reason = classify_path('Ethernet 3', '169.254.143.75', '', True, 'test')
cls2, score2, reason2 = classify_path('Wi-Fi', '192.168.1.225', '192.168.1.1', True, 'test')
ok = cls == 'invalid' and cls2 == 'recommended'
report.write_text(f"# Network Path Rules Report\n\nAPIPA: {cls} / {reason}\n\nPrivate LAN: {cls2} / {reason2}\n\nResult: {'PASS' if ok else 'FAIL'}\n", encoding='utf-8')
raise SystemExit(0 if ok else 1)
