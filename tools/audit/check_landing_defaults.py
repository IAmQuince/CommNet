import pathlib, sys
root=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(root/'src'))
from commnet.core.config_schema import DEFAULT_CONFIG
assert DEFAULT_CONFIG['commweb_landing_enabled'] is True
assert DEFAULT_CONFIG['admin_localhost_only'] is True
print('Landing defaults audit: PASS')
