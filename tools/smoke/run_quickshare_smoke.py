
from __future__ import annotations
import os, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from commnet.core.paths import RuntimePaths
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.core.config import ConfigManager
from commnet.setup.quick_setup import detect_all, create_recommended_public_folder
from commnet.share.store import ShareStore
from commnet.share.path_guard import safe_resolve, PathGuardError
from commnet.share.browser import list_entries, resolve_download

base = Path(tempfile.mkdtemp(prefix='commnet_qs_'))
os.environ['COMMNET_RUNTIME_DIR'] = str(base/'runtime')
try:
    paths = RuntimePaths(ROOT); paths.ensure_all()
    store = SQLiteStore(paths); store.initialize()
    audit = AuditLogger(paths, store)
    cfg = ConfigManager(paths).ensure_default()
    detected = detect_all()
    assert 'computer' in detected and 'lan_addresses' in detected
    share_dir = base/'public'; share_dir.mkdir(); (share_dir/'hello.txt').write_text('hello', encoding='utf-8')
    ss = ShareStore(store, audit, ROOT)
    sid = ss.add_share('Smoke Public', str(share_dir), 'SmokePublic', 'lan_visible', 'list_and_download', True, True)
    assert ss.list_shares(True)
    share = ss.get_share(sid)
    assert share is not None
    listing = list_entries(share, '')
    assert listing['entries']
    f = resolve_download(share, 'hello.txt')
    assert f.read_text(encoding='utf-8') == 'hello'
    try:
        safe_resolve(str(share_dir), '../outside.txt')
        raise AssertionError('path traversal was not blocked')
    except PathGuardError:
        pass
    ss.set_access_code('1234')
    assert ss.verify_code('1234')
    assert not ss.verify_code('wrong')
    print('QuickShare smoke: PASS')
finally:
    shutil.rmtree(base, ignore_errors=True)
