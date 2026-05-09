from __future__ import annotations

import http.client, subprocess, sys, time
from _smoke_common import ROOT, result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore

PORT=8792

def req(path,cookie=''):
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
    _,_,portal=req('/portal')
    _,_,guest_sess=req('/api/session')
    _,_,admin_sess=req('/api/session',cookie)
    checks={
        'server_ready':ready,
        'account_menu_rendered': 'id=\'account-menu\'' in portal or 'id="account-menu"' in portal,
        'dropdown_contains_profile_icon': '/account/icon' in portal,
        'guest_session_api': '"signed_in": false' in guest_sess and '"can_admin": false' in guest_sess,
        'admin_session_api': '"signed_in": true' in admin_sess and '"can_admin": true' in admin_sess,
    }
finally:
    try: req('/api/shutdown')
    except Exception: pass
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
raise SystemExit(result('account_dropdown_report.json', checks, {}))
