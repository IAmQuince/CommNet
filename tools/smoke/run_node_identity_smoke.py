import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from commnet.identity.node_identity import ensure_node_identity
cfg = {}
ensure_node_identity(cfg)
uid = cfg['commnet_user_id']
ensure_node_identity(cfg)
assert cfg['commnet_user_id'] == uid
assert uid.startswith('CommNet_')
print('Node identity smoke: PASS')
