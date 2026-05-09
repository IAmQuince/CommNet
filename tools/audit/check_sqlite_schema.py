import os, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
with tempfile.TemporaryDirectory() as td:
    old = os.environ.get('COMMNET_RUNTIME_DIR')
    os.environ['COMMNET_RUNTIME_DIR'] = td
    paths = RuntimePaths(root)
    store = SQLiteStore(paths); store.initialize()
    counts = store.table_counts()
    required = {'config_snapshots','config_changes','devices','file_roots','services','policy_rules','roles','users_local','messages'}
    missing = sorted(required - set(counts))
    if old is None: os.environ.pop('COMMNET_RUNTIME_DIR', None)
    else: os.environ['COMMNET_RUNTIME_DIR'] = old
body = '# SQLite Schema Report\n\n' + ('PASS\n' if not missing else 'FAIL missing: ' + ', '.join(missing) + '\n')
(root/'audit_reports'/'active'/'sqlite_schema_report.md').write_text(body, encoding='utf-8')
print('SQLITE_SCHEMA_' + ('PASS' if not missing else 'FAIL'))
raise SystemExit(0 if not missing else 1)
