from pathlib import Path
import sys, os, tempfile, shutil
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
req={'peers','peer_handshakes','transport_dependencies','messages','delivery_attempts','route_decisions','adapter_events','network_events'}
rt=Path(tempfile.mkdtemp(prefix='commnet_audit_schema_'))
try:
    os.environ['COMMNET_RUNTIME_DIR']=str(rt)
    store=SQLiteStore(RuntimePaths(root)); store.initialize()
    with store.connect() as conn:
        tables={r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    missing=sorted(req-tables)
finally:
    shutil.rmtree(rt, ignore_errors=True)
report=root/'audit_reports/active/network_schema_report.md'; report.parent.mkdir(parents=True,exist_ok=True)
report.write_text('# Network Schema Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: '+', '.join(missing)+'\n'), encoding='utf-8')
if missing:
    print('missing', missing); sys.exit(1)
print('NETWORK_SCHEMA_PASS')
