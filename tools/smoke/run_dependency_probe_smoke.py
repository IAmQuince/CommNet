import sys, tempfile, shutil
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.transport.dependencies import check_all_dependencies
rt=Path(tempfile.mkdtemp(prefix='commnet_dep_'))
try:
    import os; os.environ['COMMNET_RUNTIME_DIR']=str(rt)
    paths=RuntimePaths(root); store=SQLiteStore(paths); store.initialize()
    deps=check_all_dependencies(store)
    assert any(d['package_name']=='meshtastic' for d in deps)
    assert any(d['import_name']=='RNS' for d in deps)
    print('DEPENDENCY_PROBE_SMOKE_PASS')
finally:
    shutil.rmtree(rt, ignore_errors=True)
