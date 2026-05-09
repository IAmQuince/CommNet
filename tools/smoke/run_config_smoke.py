import os, sys, tempfile, json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.config import ConfigManager
with tempfile.TemporaryDirectory() as td:
    os.environ['COMMNET_RUNTIME_DIR'] = td
    paths = RuntimePaths(root)
    cm = ConfigManager(paths)
    cfg = cm.ensure_default()
    assert cfg['visibility_mode'] == 'private_local_only'
    cfg['node_name'] = 'Smoke Node'
    cfg['first_run_complete'] = True
    cm.save(cfg, snapshot=True, reason='smoke')
    assert ConfigManager(paths).load()['node_name'] == 'Smoke Node'
    idx = cm.snapshot_index()
    assert idx, 'snapshot not created'
    exported = cm.export_config_text()
    cm.import_config_text(exported)
print('CONFIG_SMOKE_PASS')
