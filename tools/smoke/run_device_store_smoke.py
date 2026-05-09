import os, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.core.device_store import DeviceStore
with tempfile.TemporaryDirectory() as td:
    os.environ['COMMNET_RUNTIME_DIR'] = td
    paths = RuntimePaths(root); store = SQLiteStore(paths); store.initialize()
    ds = DeviceStore(store, AuditLogger(paths, store))
    did = ds.add('Smoke Device', 'windows_pc', 'trusted', 'notes', ['local_loopback'])
    assert any(d['device_id'] == did for d in ds.list())
    ds.delete(did)
    assert not any(d['device_id'] == did for d in ds.list())
print('DEVICE_STORE_SMOKE_PASS')
