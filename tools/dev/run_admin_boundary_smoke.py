from __future__ import annotations

import http.client
import subprocess
import sys
import time
import uuid
from _smoke_common import ROOT, result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore

PORT = 8790


def request(path: str, method: str = 'GET', body: str = '', cookie: str = ''):
    headers = {}
    if cookie:
        headers['Cookie'] = cookie
    if method == 'POST':
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    c = http.client.HTTPConnection('127.0.0.1', PORT, timeout=2)
    c.request(method, path, body=body.encode('utf-8'), headers=headers)
    r = c.getresponse(); data = r.read().decode('utf-8','replace'); headers = dict(r.getheaders()); c.close()
    return r.status, headers, data

paths = runtime(); store = SQLiteStore(paths); store.initialize(); audit = AuditLogger(paths, store); us = UserStore(store, audit); us.ensure_default_admin()
# Create an ordinary guest/user that must not get admin access.
guest_name = ('guest' + uuid.uuid4().hex[:10])[:32]
guest_id = us.create_user(guest_name, 'Portal Guest', 'guestpass1', 'user', 'guest smoke')
guest_session = us.create_session(guest_id, '127.0.0.1', 'smoke')
admin = us.authenticate('admin', 'password', '127.0.0.1', 'smoke')
admin_session = admin['session_id']
proc = subprocess.Popen([sys.executable, str(ROOT/'src/commnet/main.py'), 'serve', '--host', '127.0.0.1', '--port', str(PORT)], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
try:
    ready = False
    for _ in range(40):
        try:
            st, _, _ = request('/api/status')
            if st == 200:
                ready = True; break
        except Exception:
            time.sleep(0.2)
    anon_status, anon_headers, anon_body = request('/admin/hud')
    guest_status, _, guest_body = request('/admin/hud', cookie='commnet_session=' + guest_session)
    admin_status, _, admin_body = request('/admin/hud', cookie='commnet_session=' + admin_session)
    sess_status, _, sess_body = request('/api/session', cookie='commnet_session=' + admin_session)
    checks = {
        'server_ready': ready,
        'anonymous_redirected_to_login': anon_status in (301,302) and '/login' in anon_headers.get('Location',''),
        'guest_denied_admin_hud': guest_status == 403 and 'Admin HUD access denied' in guest_body,
        'admin_allowed_admin_hud': admin_status == 200 and 'CommNet Admin HUD' in admin_body,
        'admin_session_reports_can_admin': sess_status == 200 and '"can_admin": true' in sess_body,
    }
finally:
    try:
        request('/api/shutdown')
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()
raise SystemExit(result('admin_boundary_report.json', checks, {}))
