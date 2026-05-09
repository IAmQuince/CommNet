import sys, tempfile, shutil, os
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.peer_store import PeerStore
rt=Path(tempfile.mkdtemp(prefix='commnet_peer_'))
try:
    os.environ['COMMNET_RUNTIME_DIR']=str(rt)
    store=SQLiteStore(RuntimePaths(root)); store.initialize(); ps=PeerStore(store)
    pid=ps.add('Peer','http://127.0.0.1:8766','known','notes')
    assert ps.get(pid)['display_name']=='Peer'
    ps.set_trust(pid,'trusted'); assert ps.get(pid)['trust_state']=='trusted'
    ps.record_handshake(pid,'failed',{'reason':'offline'}); assert ps.get(pid)['last_status']=='failed'
    ps.delete(pid); assert ps.get(pid) is None
    print('PEER_STORE_SMOKE_PASS')
finally:
    shutil.rmtree(rt, ignore_errors=True)
