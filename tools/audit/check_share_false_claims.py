import pathlib
root=pathlib.Path(__file__).resolve().parents[2]
text=(root/'README.md').read_text(errors='ignore') + (root/'RUN_STATUS.md').read_text(errors='ignore')
for bad in ['production authentication is complete','forces all Wi-Fi users','automatic router configuration works']:
    assert bad.lower() not in text.lower()
print('Share false-claims audit: PASS')
