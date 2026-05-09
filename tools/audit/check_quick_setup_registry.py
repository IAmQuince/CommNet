import json, pathlib
root=pathlib.Path(__file__).resolve().parents[2]
assert (root/'registries/quick_setup_modes.json').exists()
print('Quick setup registry audit: PASS')
