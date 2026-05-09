from __future__ import annotations
import json, subprocess, sys, time, urllib.request, webbrowser
from pathlib import Path
from tkinter import Tk, StringVar, Button, Label, Text, END, DISABLED, NORMAL, Frame, BOTH, LEFT, RIGHT, X
DEFAULT_HOST='127.0.0.1'; DEFAULT_PORT=8765

def _url(path:str='/api/status')->str: return f'http://{DEFAULT_HOST}:{DEFAULT_PORT}{path}'
def _fetch_status()->dict:
    try:
        with urllib.request.urlopen(_url('/api/status'), timeout=1.5) as resp: return json.loads(resp.read().decode('utf-8','replace'))
    except Exception as exc: return {'running':False,'error':str(exc)}
class CommNetControlWindow:
    def __init__(self, package_root:Path):
        self.package_root=package_root; self.main_py=package_root/'src'/'commnet'/'main.py'; self.proc=None
        self.root=Tk(); self.root.title('CommNet Control'); self.root.geometry('720x480'); self.root.minsize(560,360)
        self.status=StringVar(value='Starting CommNet...'); self.detail=StringVar(value='')
        Label(self.root,text='CommNet Control',font=('Segoe UI',16,'bold')).pack(anchor='w',padx=12,pady=(12,2)); Label(self.root,textvariable=self.status,font=('Segoe UI',11)).pack(anchor='w',padx=12); Label(self.root,textvariable=self.detail,font=('Consolas',9),justify=LEFT).pack(anchor='w',padx=12,pady=(0,8))
        btns=Frame(self.root); btns.pack(fill=X,padx=12,pady=6)
        Button(btns,text='Open Admin HUD',command=lambda:webbrowser.open(_url('/admin/hud'))).pack(side=LEFT,padx=4); Button(btns,text='Open Portal',command=lambda:webbrowser.open(_url('/portal'))).pack(side=LEFT,padx=4); Button(btns,text='Diagnostics',command=lambda:webbrowser.open(_url('/admin/diagnostics'))).pack(side=LEFT,padx=4); Button(btns,text='Copy Invite',command=self.copy_invite).pack(side=LEFT,padx=4); Button(btns,text='Stop Server',command=self.stop_server).pack(side=RIGHT,padx=4)
        self.log=Text(self.root,height=16,wrap='word'); self.log.pack(fill=BOTH,expand=True,padx=12,pady=8)
        self.log_msg('Controller started. Keep this window open or minimized while the server is running.'); self.ensure_server(); self.root.after(1000,self.poll)
    def log_msg(self,msg:str)->None:
        self.log.configure(state=NORMAL); self.log.insert(END,time.strftime('%H:%M:%S')+'  '+msg+'\n'); self.log.see(END); self.log.configure(state=DISABLED)
    def ensure_server(self)->None:
        st=_fetch_status()
        if st.get('running') or st.get('status')=='ok': self.log_msg('Existing server detected.'); return
        self.log_msg('Launching CommNet server process...'); logs=self.package_root/'runtime'/'logs'; logs.mkdir(parents=True,exist_ok=True)
        out=open(logs/'control_window_server_stdout.log','ab'); err=open(logs/'control_window_server_stderr.log','ab')
        self.proc=subprocess.Popen([sys.executable,str(self.main_py),'serve','--host',DEFAULT_HOST,'--port',str(DEFAULT_PORT)],cwd=str(self.package_root),stdout=out,stderr=err,stdin=subprocess.DEVNULL)
    def poll(self)->None:
        st=_fetch_status()
        if st.get('running') or st.get('status')=='ok': self.status.set('Status: RUNNING'); self.detail.set(f"Admin: {_url('/admin/hud')}\nPortal: {_url('/portal')}\nStop: use this window or Stop_CommNet.bat")
        else: self.status.set('Status: NOT REACHABLE'); self.detail.set(st.get('error','No status available'))
        self.root.after(2500,self.poll)
    def copy_invite(self)->None:
        url=_url('/portal')
        try: self.root.clipboard_clear(); self.root.clipboard_append(url); self.log_msg('Copied portal URL to clipboard: '+url)
        except Exception as exc: self.log_msg('Clipboard failed: '+str(exc))
    def stop_server(self)->None:
        self.log_msg('Sending shutdown request...')
        try: urllib.request.urlopen(_url('/api/shutdown'),timeout=3).read()
        except Exception as exc: self.log_msg('Shutdown request returned: '+str(exc))
        self.root.after(800,self.root.destroy)
    def run(self)->int: self.root.mainloop(); return 0
def main()->int: return CommNetControlWindow(Path(__file__).resolve().parents[2]).run()
if __name__=='__main__': raise SystemExit(main())
