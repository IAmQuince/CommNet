from __future__ import annotations
import http.client, subprocess, sys, time
from _smoke_common import ROOT, result
proc=subprocess.Popen([sys.executable,str(ROOT/'src/commnet/main.py'),'serve','--host','127.0.0.1','--port','8789'],cwd=str(ROOT),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
    ok=False; body=''
    for _ in range(40):
        try:
            c=http.client.HTTPConnection('127.0.0.1',8789,timeout=1); c.request('GET','/portal'); r=c.getresponse(); body=r.read().decode('utf-8','replace'); ok=(r.status==200); c.close()
            if ok: break
        except Exception: time.sleep(0.2)
    checks={'portal_returns_200':ok,'portal_grid_present':'portal-grid' in body,'not_admin_rail_layout':'admin-rail' not in body,'retroweb_card_present':'RetroWeb' in body,'bbs_card_present':'BBS' in body}
finally:
    try:
        c=http.client.HTTPConnection('127.0.0.1',8789,timeout=1); c.request('GET','/api/shutdown'); c.getresponse().read(); c.close()
    except Exception: pass
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
raise SystemExit(result('portal_grid_smoke_report.json', checks, {'body_length':len(body)}))
