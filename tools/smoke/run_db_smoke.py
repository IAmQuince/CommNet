import os, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
with tempfile.TemporaryDirectory() as td:
    os.environ['COMMNET_RUNTIME_DIR'] = td
    paths = RuntimePaths(root)
    store = SQLiteStore(paths)
    store.initialize()
    assert store.integrity_check() == 'ok'
    counts = store.table_counts()
    assert 'messages' in counts
print('DB_SMOKE_PASS')
