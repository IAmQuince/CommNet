import sys, tempfile, shutil, os
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.peer_store import PeerStore
from commnet.transport.registry import build_default_registry
from commnet.transport.engine import DeliveryEngine
from commnet.transport.messages import MessageEnvelope
rt=Path(tempfile.mkdtemp(prefix='commnet_delivery_'))
try:
    os.environ['COMMNET_RUNTIME_DIR']=str(rt)
    store=SQLiteStore(RuntimePaths(root)); store.initialize(); ps=PeerStore(store)
    engine=DeliveryEngine(build_default_registry(ps), None, store)
    msg=MessageEnvelope.create('text_message','hello','self')
    res=engine.send(msg)
    assert res.success
    assert store.table_counts()['messages'] >= 1
    assert store.table_counts()['route_decisions'] >= 1
    assert store.table_counts()['delivery_attempts'] >= 1
    print('DELIVERY_ENGINE_SMOKE_PASS')
finally:
    shutil.rmtree(rt, ignore_errors=True)
