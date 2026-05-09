import os, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.config import ConfigManager
from commnet.policy.privacy import is_private
from commnet.policy.services import service_visible
with tempfile.TemporaryDirectory() as td:
    os.environ['COMMNET_RUNTIME_DIR'] = td
    cfg = ConfigManager(RuntimePaths(root)).ensure_default()
    assert is_private(cfg)
    assert service_visible(cfg, 'emergency')
print('POLICY_SMOKE_PASS')
