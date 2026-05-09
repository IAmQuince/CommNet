import os, shutil, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.peer_store import PeerStore
from commnet.transport.adapters_lan import LanHttpAdapter
from commnet.transport.messages import MessageEnvelope
rt=Path(tempfile.mkdtemp(prefix='commnet_lan_'))
try:
    os.environ['COMMNET_RUNTIME_DIR']=str(rt)
    store=SQLiteStore(RuntimePaths(root)); store.initialize(); ps=PeerStore(store)
    adapter=LanHttpAdapter(ps, timeout=0.2)
    status=adapter.probe()
    assert status.available
    msg=MessageEnvelope.create('text_message','hello','peer_missing')
    res=adapter.send(msg)
    assert not res.success and 'not found' in res.detail.lower()
    print('LAN_ADAPTER_SMOKE_PASS')
finally:
    shutil.rmtree(rt, ignore_errors=True)
