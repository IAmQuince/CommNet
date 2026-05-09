from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from commnet.transport.adapters_catena import CatenaSerialLoRaAdapter
root=Path(__file__).resolve().parents[2]
ad=CatenaSerialLoRaAdapter(fake=True)
results=[ad.ping('abc'), ad.identify(), ad.status_request(), ad.configure_radio(), ad.send_text('msg_002','text_message','Hello')]
ok=all(r.get('ok') for r in results) and results[-1].get('semantics')=='local_hardware_ack_only'
(root/'proof'/'catena_real_adapter_fakeport_smoke_report.md').write_text('# Catena Real Adapter Fake-Port Smoke\n\nResult: '+('PASS' if ok else 'FAIL')+'\n', encoding='utf-8')
raise SystemExit(0 if ok else 1)
