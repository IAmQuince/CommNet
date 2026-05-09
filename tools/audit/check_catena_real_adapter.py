from __future__ import annotations
from pathlib import Path
root=Path(__file__).resolve().parents[2]
text=(root/'src'/'commnet'/'transport'/'adapters_catena.py').read_text(encoding='utf-8')
ok='import serial  # type: ignore' in text and 'def _transact_real' in text and 'expected_response_types' in text
report=root/'audit_reports'/'active'/'catena_real_adapter_report.md'
report.write_text(f"# Catena Real Adapter Report\n\nLazy serial import and real transaction code present: {ok}\n\nResult: {'PASS' if ok else 'FAIL'}\n", encoding='utf-8')
raise SystemExit(0 if ok else 1)
