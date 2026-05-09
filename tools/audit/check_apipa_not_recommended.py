from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from commnet.network.path_selector import classify_path
root = Path(__file__).resolve().parents[2]
report = root/'audit_reports'/'active'/'apipa_not_recommended_report.md'
cls, score, reason = classify_path('test','169.254.1.2','',True,'test')
ok = cls == 'invalid' and score < 0
report.write_text(f"# APIPA Not Recommended Report\n\n169.254.1.2 classification: {cls}\nReason: {reason}\nResult: {'PASS' if ok else 'FAIL'}\n", encoding='utf-8')
raise SystemExit(0 if ok else 1)
