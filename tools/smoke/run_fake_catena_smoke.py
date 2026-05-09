import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from commnet.transport.adapters_catena import CatenaSerialLoRaAdapter
ad = CatenaSerialLoRaAdapter(fake=True)
assert ad.ping()['ok']
assert ad.identify()['ok']
res = ad.send_text('m1','text_message','hello')
assert res['ok']
assert res['semantics'] == 'local_hardware_ack_only'
print('Fake Catena smoke: PASS')
