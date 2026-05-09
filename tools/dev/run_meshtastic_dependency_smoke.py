from _smoke_common import runtime, result
from commnet.core.db import SQLiteStore
from commnet.hardware.meshtastic_probe import dependency_status, list_candidate_ports, latest_status
paths=runtime(); store=SQLiteStore(paths); store.initialize(); deps=dependency_status(); ports=list_candidate_ports(); latest=latest_status(store)
raise SystemExit(result('meshtastic_dependency_smoke_report.json', {'dependency_check_returns_state':bool(deps.get('state')),'ports_check_returns_list':isinstance(ports,list),'latest_status_returns_state':bool(latest.get('state'))}, {'dependency':deps,'ports':ports[:5],'latest':latest}))
