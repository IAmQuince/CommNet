import json, pathlib
root=pathlib.Path(__file__).resolve().parents[2]
data=json.loads((root/'registries/share_permission_profiles.json').read_text())
assert 'list_and_download' in data['profiles'] and 'dropbox_upload_only' in data['profiles']
print('Permission profile audit: PASS')
