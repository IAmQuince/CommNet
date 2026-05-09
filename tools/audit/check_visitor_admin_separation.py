import pathlib
root=pathlib.Path(__file__).resolve().parents[2]
app=(root/'src/commnet/server/app.py').read_text()
assert 'visitor_admin_blocked' in app and 'not self.is_local_client()' in app
print('Visitor/admin separation audit: PASS')
