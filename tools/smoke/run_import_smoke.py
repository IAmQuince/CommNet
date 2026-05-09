import sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'src'))
modules = [
    'commnet.main', 'commnet.core.paths', 'commnet.core.config', 'commnet.core.db',
    'commnet.server.app', 'commnet.transport.registry', 'commnet.transport.engine', 'commnet.core.config_schema', 'commnet.core.device_store', 'commnet.core.file_roots', 'commnet.policy.gate'
]
for name in modules:
    __import__(name)
print('IMPORT_SMOKE_PASS')
