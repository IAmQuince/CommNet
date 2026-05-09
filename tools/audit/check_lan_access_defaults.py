import pathlib, sys
root=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(root/'src'))
from commnet.core.config_schema import DEFAULT_CONFIG
assert DEFAULT_CONFIG['lan_access_enabled'] is False
assert DEFAULT_CONFIG['lan_access_mode'] == 'localhost_only'
assert DEFAULT_CONFIG['default_share_visibility'] == 'private'
assert DEFAULT_CONFIG['access_code_required_default'] is True
print('LAN access defaults audit: PASS')
