import os, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.config import ConfigManager
from commnet.core.service_store import portal_services, sync_services_to_db
with tempfile.TemporaryDirectory() as td:
    os.environ['COMMNET_RUNTIME_DIR'] = td
    paths = RuntimePaths(root)
    store = SQLiteStore(paths); store.initialize()
    cfg = ConfigManager(paths).ensure_default()
    sync_services_to_db(store, cfg)
    visible = portal_services(cfg)
    assert any(s['service_id'] == 'emergency' for s in visible)
print('SERVICES_SMOKE_PASS')
