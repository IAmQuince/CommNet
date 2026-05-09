from __future__ import annotations

import http.client, subprocess, sys, time, urllib.parse
from _smoke_common import ROOT, result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.core.config import ConfigManager
from commnet.ux.ui_config import UI_DEFAULTS
from commnet.identity.user_store import UserStore

PORT=8793

def req(path,method='GET',body='',cookie=''):
    headers={}
    if cookie: headers['Cookie']=cookie
    if method=='POST': headers['Content-Type']='application/x-www-form-urlencoded'
    c=http.client.HTTPConnection('127.0.0.1',PORT,timeout=2); c.request(method,path,body=body.encode('utf-8'),headers=headers); r=c.getresponse(); data=r.read().decode('utf-8','replace'); h=dict(r.getheaders()); c.close(); return r.status,h,data
paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths,store); cfg_mgr=ConfigManager(paths); cfg=cfg_mgr.ensure_default(); original_ui=cfg.get('ui')
us=UserStore(store,audit); us.ensure_default_admin(); admin=us.authenticate('admin','password','127.0.0.1','smoke'); cookie='commnet_session='+admin['session_id']
proc=subprocess.Popen([sys.executable,str(ROOT/'src/commnet/main.py'),'serve','--host','127.0.0.1','--port',str(PORT)],cwd=str(ROOT),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
    ready=False
    for _ in range(40):
        try:
            st,_,_=req('/api/status')
            if st==200: ready=True; break
        except Exception: time.sleep(.2)
    body=urllib.parse.urlencode({'theme':'dark','card_density':'dense','icon_mode':'emoji','show_unavailable_guest_apps':'grayed'})
    post_status, post_headers, _ = req('/account/settings','POST',body,cookie)
    _,_,portal=req('/portal',cookie=cookie)
    _,_,bbs=req('/bbs',cookie=cookie)
    _,_,rw=req('/retroweb',cookie=cookie)
    checks={
        'server_ready':ready,
        'settings_post_redirects':post_status in (301,302),
        'portal_theme_dark': 'theme-dark' in portal and 'density-dense' in portal,
        'bbs_theme_dark': 'theme-dark' in bbs and 'density-dense' in bbs,
        'retroweb_theme_dark': 'theme-dark' in rw and 'density-dense' in rw,
    }
finally:
    try:
        cfg=cfg_mgr.load(); cfg['ui']=original_ui if isinstance(original_ui,dict) else dict(UI_DEFAULTS); cfg_mgr.save(cfg,snapshot=True,reason='user_settings_route_smoke_restore')
    except Exception: pass
    try: req('/api/shutdown')
    except Exception: pass
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
raise SystemExit(result('user_settings_route_report.json', checks, {}))
