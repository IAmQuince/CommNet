from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from _smoke_common import result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.share.store import ShareStore
from commnet.share.browser import list_entries, resolve_download
from commnet.share.preview import resolve_preview, read_text_preview

paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths, store); ss=ShareStore(store, audit, paths.package_root)
with tempfile.TemporaryDirectory() as td:
    root=Path(td); (root/'hello.txt').write_text('hello preview', encoding='utf-8')
    vname='SmokeShare_' + uuid.uuid4().hex[:8]
    sid=ss.add_share('Smoke Share', str(root), vname, 'lan_visible', 'preview_only', True, False, 'preview_only', True)
    share=ss.get_share(sid)
    entries=list_entries(share)
    preview_path, kind=resolve_preview(share,'hello.txt')
    text=read_text_preview(preview_path)
    download_blocked=False
    try:
        resolve_download(share,'hello.txt')
    except PermissionError:
        download_blocked=True
    ss.update_share_policy(sid, 'lan_visible', 'list_and_download', 'download', True, False, True)
    share2=ss.get_share(sid)
    dl=resolve_download(share2,'hello.txt')
checks={'share_created': bool(sid), 'list_works': entries['entries'][0]['name']=='hello.txt', 'preview_text': kind=='text' and 'hello' in text, 'download_blocked_in_preview_mode': download_blocked, 'download_enabled_after_policy_update': dl.name=='hello.txt'}
raise SystemExit(result('share_policy_report.json', checks, {'share_id': sid}))
