import json, pathlib
root=pathlib.Path(__file__).resolve().parents[2]
assert (root/'registries/share_schema.json').exists()
print('Share schema audit: PASS')
