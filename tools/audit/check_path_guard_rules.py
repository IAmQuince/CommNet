import pathlib, sys
root=pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0,str(root/'src'))
from commnet.share.path_guard import safe_resolve, PathGuardError
try:
    safe_resolve(str(root), '../x')
    raise SystemExit('FAIL path traversal')
except PathGuardError:
    print('Path guard audit: PASS')
