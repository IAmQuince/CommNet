import sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.transport.registry import build_default_registry
from commnet.transport.messages import MessageEnvelope
from commnet.transport.planner import RoutePlanner
reg=build_default_registry(); planner=RoutePlanner(reg)
msg=MessageEnvelope.create('text_message','hello','self')
chosen, estimates=planner.choose_route(msg)
assert chosen and chosen.adapter_id=='local_loopback'
msg2=MessageEnvelope.create('text_message','hello','peer_abc')
chosen2, estimates2=planner.choose_route(msg2)
assert chosen2 and chosen2.adapter_id=='lan_http'
print('ROUTE_PLANNER_SMOKE_PASS')
