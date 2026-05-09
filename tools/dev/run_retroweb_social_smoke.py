from _smoke_common import runtime, result
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore
from commnet.retroweb.store import RetroWebStore, render_icon
paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths,store); us=UserStore(store,audit); us.ensure_default_admin(); admin=us.get_by_username('admin'); rw=RetroWebStore(store,audit); rw.create_or_update_profile(admin['user_id'],'admin','CommNet Admin','Local RetroWeb admin profile.',{'palette':'arcade','shape':'orb','glyph':'A','pattern':'rings'}); profile=rw.profile_for_user(admin['user_id']); pid=rw.post(admin['user_id'],'Smoke RetroWeb post'); rw.comment(pid,admin['user_id'],'Smoke comment'); feed=rw.feed(); comments=rw.comments_for(pid); icon=render_icon(profile.get('icon_json'),32) if profile else ''
raise SystemExit(result('retroweb_social_smoke_report.json', {'profile_created':bool(profile and profile.get('handle')=='admin'),'icon_renders':'rw-icon' in icon,'post_created':any(p.get('post_id')==pid for p in feed),'comment_created':len(comments)>=1}, {'post_id':pid}))
