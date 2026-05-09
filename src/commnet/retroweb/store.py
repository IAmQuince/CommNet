from __future__ import annotations
import json, uuid
from typing import Any
PALETTES={'midnight':['#0f172a','#334155','#38bdf8','#e0f2fe'],'crt_green':['#001b10','#024d2b','#00ff88','#b7ffd9'],'sunset':['#33111d','#7f1d1d','#f97316','#fde68a'],'arcade':['#18181b','#7c3aed','#22d3ee','#f0abfc']}
DEFAULT_ICON={'palette':'arcade','shape':'orb','glyph':'★','pattern':'rings'}
class RetroWebStore:
    def __init__(self, store, audit=None): self.store=store; self.audit=audit; self.store.initialize()
    def profile_for_user(self,user_id:str)->dict[str,Any]|None:
        if not user_id: return None
        with self.store.connect() as conn: row=conn.execute('SELECT * FROM retroweb_profiles WHERE user_id=?',(user_id,)).fetchone()
        if not row: return None
        d=dict(row)
        try: d['icon_json']=json.loads(d.get('icon_json') or '{}')
        except Exception: d['icon_json']=dict(DEFAULT_ICON)
        return d
    def create_or_update_profile(self,user_id:str,handle:str,display_name:str,about:str,icon:dict[str,Any])->None:
        handle=''.join(ch for ch in (handle or '').strip().lower() if ch.isalnum() or ch in '_.-')[:32] or ('user_'+user_id[-6:])
        display_name=(display_name or handle).strip()[:64]; about=(about or '').strip()[:500]
        clean={'palette':icon.get('palette') if icon.get('palette') in PALETTES else DEFAULT_ICON['palette'],'shape':icon.get('shape') if icon.get('shape') in {'orb','diamond','square','capsule'} else DEFAULT_ICON['shape'],'glyph':(icon.get('glyph') or DEFAULT_ICON['glyph'])[:2],'pattern':icon.get('pattern') if icon.get('pattern') in {'rings','grid','burst','plain'} else DEFAULT_ICON['pattern']}
        with self.store.connect() as conn:
            conn.execute('''INSERT INTO retroweb_profiles(user_id,handle,display_name,about,icon_json) VALUES (?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET handle=excluded.handle, display_name=excluded.display_name, about=excluded.about, icon_json=excluded.icon_json, updated_at=CURRENT_TIMESTAMP''',(user_id,handle,display_name,about,json.dumps(clean,sort_keys=True))); conn.commit()
        if self.audit: self.audit.write('retroweb_profile_saved', {'user_id':user_id,'handle':handle})
    def profiles(self, limit:int=100)->list[dict[str,Any]]:
        with self.store.connect() as conn: rows=conn.execute('SELECT * FROM retroweb_profiles ORDER BY updated_at DESC LIMIT ?',(limit,)).fetchall()
        out=[]
        for r in rows:
            d=dict(r)
            try: d['icon_json']=json.loads(d.get('icon_json') or '{}')
            except Exception: d['icon_json']=dict(DEFAULT_ICON)
            out.append(d)
        return out
    def post(self,user_id:str,body:str,visibility:str='retroweb')->str:
        body=(body or '').strip()[:1200]
        if not body: raise ValueError('RetroWeb post body is required.')
        pid='rwpost_'+uuid.uuid4().hex[:12]
        with self.store.connect() as conn: conn.execute('INSERT INTO retroweb_posts(post_id,user_id,body,visibility) VALUES (?,?,?,?)',(pid,user_id,body,visibility[:20])); conn.commit()
        if self.audit: self.audit.write('retroweb_post_created', {'post_id':pid,'user_id':user_id})
        return pid
    def comment(self,post_id:str,user_id:str,body:str)->str:
        body=(body or '').strip()[:800]
        if not body: raise ValueError('Comment body is required.')
        cid='rwcomment_'+uuid.uuid4().hex[:12]
        with self.store.connect() as conn: conn.execute('INSERT INTO retroweb_comments(comment_id,post_id,user_id,body) VALUES (?,?,?,?)',(cid,post_id,user_id,body)); conn.commit()
        if self.audit: self.audit.write('retroweb_comment_created', {'post_id':post_id,'comment_id':cid,'user_id':user_id})
        return cid
    def feed(self,limit:int=50)->list[dict[str,Any]]:
        with self.store.connect() as conn: rows=conn.execute('''SELECT p.*, rp.handle, rp.display_name, rp.icon_json, COUNT(c.comment_id) AS comment_count FROM retroweb_posts p LEFT JOIN retroweb_profiles rp ON rp.user_id=p.user_id LEFT JOIN retroweb_comments c ON c.post_id=p.post_id WHERE p.status='published' GROUP BY p.post_id ORDER BY p.created_at DESC LIMIT ?''',(limit,)).fetchall()
        out=[]
        for r in rows:
            d=dict(r)
            try: d['icon_json']=json.loads(d.get('icon_json') or '{}')
            except Exception: d['icon_json']=dict(DEFAULT_ICON)
            out.append(d)
        return out
    def comments_for(self,post_id:str)->list[dict[str,Any]]:
        with self.store.connect() as conn: rows=conn.execute('''SELECT c.*, rp.handle, rp.display_name, rp.icon_json FROM retroweb_comments c LEFT JOIN retroweb_profiles rp ON rp.user_id=c.user_id WHERE c.post_id=? AND c.status='published' ORDER BY c.created_at ASC''',(post_id,)).fetchall()
        out=[]
        for r in rows:
            d=dict(r)
            try: d['icon_json']=json.loads(d.get('icon_json') or '{}')
            except Exception: d['icon_json']=dict(DEFAULT_ICON)
            out.append(d)
        return out

def render_icon(icon:dict[str,Any],size:int=56)->str:
    icon=icon or DEFAULT_ICON; palette=PALETTES.get(icon.get('palette'),PALETTES[DEFAULT_ICON['palette']]); glyph=(icon.get('glyph') or DEFAULT_ICON['glyph'])[:2]; shape=icon.get('shape') or 'orb'; radius='50%' if shape=='orb' else ('12px' if shape in {'square','diamond'} else '999px'); rotate=' transform:rotate(45deg);' if shape=='diamond' else ''; inner=' transform:rotate(-45deg); display:inline-block;' if shape=='diamond' else ''
    return f"<span class='rw-icon' style='width:{size}px;height:{size}px;border-radius:{radius};background:linear-gradient(135deg,{palette[1]},{palette[2]});border:2px solid {palette[3]};{rotate}'><span style='{inner}'>{glyph}</span></span>"
