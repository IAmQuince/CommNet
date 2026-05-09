import os, shutil, sys, tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.peer_store import PeerStore
from commnet.transport.dependencies import check_all_dependencies
from commnet.transport.registry import build_default_registry
from commnet.transport.planner import RoutePlanner
from commnet.transport.engine import DeliveryEngine
from commnet.transport.messages import MessageEnvelope
from commnet.transport.adapters_lan import LanHttpAdapter
rt=Path(tempfile.mkdtemp(prefix='commnet_network_'))
try:
    os.environ['COMMNET_RUNTIME_DIR']=str(rt)
    paths=RuntimePaths(root); store=SQLiteStore(paths); store.initialize(); ps=PeerStore(store)
    deps=check_all_dependencies(store); assert any(d['package_name']=='meshtastic' for d in deps)
    pid=ps.add('Peer','http://127.0.0.1:8766','known','network smoke'); assert ps.get(pid)
    reg=build_default_registry(ps); planner=RoutePlanner(reg)
    msg=MessageEnvelope.create('text_message','hello','self'); chosen,_=planner.choose_route(msg); assert chosen.adapter_id=='local_loopback'
    res=DeliveryEngine(reg,None,store).send(msg); assert res.success
    lan=LanHttpAdapter(ps); assert lan.probe().available
    assert store.table_counts()['route_decisions'] >= 1
    print('DEPENDENCY_PROBE_SMOKE_PASS')
    print('PEER_STORE_SMOKE_PASS')
    print('ROUTE_PLANNER_SMOKE_PASS')
    print('DELIVERY_ENGINE_SMOKE_PASS')
    print('LAN_ADAPTER_SMOKE_PASS')
    print('NETWORK_SMOKE_PASS')
finally:
    shutil.rmtree(rt, ignore_errors=True)
