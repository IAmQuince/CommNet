from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from commnet.hardware.catena_protocol import split_cmn1_frames, parse_line, delivery_semantics
root=Path(__file__).resolve().parents[2]
raw='CMN1|STATUS|uptime_ms=5000CMN1|ACK|id=msg_002|status=accepted|detail=local_hardware_ack_only\n'
frames=split_cmn1_frames(raw)
parsed=[parse_line(f) for f in frames]
ok=len(frames)==2 and parsed[1]['type']=='ACK' and delivery_semantics(parsed[1])=='local_hardware_ack_only'
(root/'proof'/'catena_transcript_smoke_report.md').write_text(f"# Catena Transcript Smoke\n\nFrames: {frames}\nResult: {'PASS' if ok else 'FAIL'}\n", encoding='utf-8')
raise SystemExit(0 if ok else 1)
