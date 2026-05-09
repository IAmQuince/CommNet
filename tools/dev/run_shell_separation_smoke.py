from __future__ import annotations

import http.client
import subprocess
import sys
import time
from _smoke_common import ROOT, result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore

PORT = 8791

def req(path, cookie=''):
    headers={}
    if cookie: headers['Cookie']=cookie
    c=http.client.HTTPConnection('127.0.0.1',PORT,timeout=2); c.request('GET',path,headers=headers); r=c.getresponse(); data=r.read().decode('utf-8','replace'); h=dict(r.getheaders()); c.close(); return r.status,h,data

paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths,store); us=UserStore(store,audit); us.ensure_default_admin(); admin=us.authenticate('admin','password','127.0.0.1','smoke'); cookie='commnet_session='+admin['session_id']
proc=subprocess.Popen([sys.executable,str(ROOT/'src/commnet/main.py'),'serve','--host','127.0.0.1','--port',str(PORT)],cwd=str(ROOT),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
    ready=False
    for _ in range(40):
        try:
            st,_,_=req('/api/status')
            if st==200: ready=True; break
        except Exception: time.sleep(.2)
    ps,_,portal=req('/portal')
    ads,_,admin=req('/admin/hud',cookie)
    checks={
        'server_ready':ready,
        'portal_uses_portal_shell':ps==200 and 'portal-shell' in portal and 'COMMNET PORTAL' in portal,
        'portal_has_sidebar': 'portal-rail' in portal and 'Account Settings' in portal,
        'portal_not_admin_area': 'ADMIN AREA' not in portal,
        'admin_uses_admin_shell': ads==200 and 'admin-shell' in admin and 'ADMIN AREA' in admin,
        'admin_has_switch_to_portal': 'Switch to CommNet Portal' in admin,
    }
finally:
    try: req('/api/shutdown')
    except Exception: pass
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
raise SystemExit(result('shell_separation_report.json', checks, {}))
