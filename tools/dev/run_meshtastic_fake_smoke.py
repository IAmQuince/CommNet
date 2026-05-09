from _smoke_common import runtime, result
from commnet.core.db import SQLiteStore
from commnet.transport.meshtastic_adapter import FakeMeshtasticAdapter
from commnet.hardware.meshtastic_probe import record_event, latest_status
paths=runtime(); store=SQLiteStore(paths); store.initialize(); adapter=FakeMeshtasticAdapter(store); probe=adapter.probe(); sent=adapter.send_text('CMN1|PING|fake=1'); record_event(store,'fake_smoke',sent,sent.get('state','simulated_sent')); latest=latest_status(store)
raise SystemExit(result('meshtastic_fake_smoke_report.json', {'fake_probe_ok':probe.get('ok') is True,'fake_send_ok':sent.get('ok') is True,'event_recorded':latest.get('last_event')=='fake_smoke'}, {'probe':probe,'sent':sent,'latest':latest}))
