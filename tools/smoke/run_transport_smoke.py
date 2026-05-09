import os, sys, tempfile, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.transport.registry import build_default_registry
from commnet.transport.engine import DeliveryEngine
from commnet.transport.messages import MessageEnvelope
with tempfile.TemporaryDirectory() as td:
    os.environ['COMMNET_RUNTIME_DIR'] = td
    paths = RuntimePaths(root)
    store = SQLiteStore(paths); store.initialize()
    engine = DeliveryEngine(build_default_registry(), AuditLogger(paths, store), store)
    msg = MessageEnvelope.create('text_message', 'smoke', 'self')
    result = engine.send(msg)
    assert result.success, result
print('TRANSPORT_SMOKE_PASS')
