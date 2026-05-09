import pathlib
root=pathlib.Path(__file__).resolve().parents[2]
text='\n'.join(p.read_text(errors='ignore') for p in (root/'docs/active').glob('*.md'))
assert 'guidance' in text.lower() or 'assist' in text.lower()
print('Captive claims audit: PASS')
