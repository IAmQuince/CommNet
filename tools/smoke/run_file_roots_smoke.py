import os, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.core.file_roots import FileRootStore
with tempfile.TemporaryDirectory() as td:
    os.environ['COMMNET_RUNTIME_DIR'] = td
    paths = RuntimePaths(root); store = SQLiteStore(paths); store.initialize()
    fs = FileRootStore(store, AuditLogger(paths, store))
    rid = fs.add('Smoke Root', r'C:\\CommNetSmoke', 'private', False, True, True)
    assert any(r['root_id'] == rid for r in fs.list())
    fs.delete(rid)
    assert not any(r['root_id'] == rid for r in fs.list())
print('FILE_ROOTS_SMOKE_PASS')
