import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from commnet.hardware.catena_protocol import make_ping, make_tx, parse_line, delivery_semantics
line = make_ping('abc')
assert parse_line('CMN1|PONG|nonce=abc')['type'] == 'PONG'
tx = make_tx('m1','text_message','hello')
assert 'body=' in tx
ack = parse_line('CMN1|ACK|id=m1|status=accepted')
assert delivery_semantics(ack) == 'local_hardware_ack_only'
print('Catena protocol smoke: PASS')
