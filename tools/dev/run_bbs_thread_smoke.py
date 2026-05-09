from _smoke_common import runtime, result
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.bbs.store import BBSStore
paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths,store); bbs=BBSStore(store,audit); bbs.ensure_seed(); boards=bbs.boards(); welcome=[t for t in bbs.threads('announcements') if t.get('seed_key')=='welcome']; tid=bbs.create_thread('general','Smoke thread','Smoke body','smoke_user'); bbs.reply(tid,'Smoke reply','smoke_user'); thread=bbs.thread(tid); replies=bbs.replies(tid)
raise SystemExit(result('bbs_thread_smoke_report.json', {'boards_seeded':len(boards)>=5,'welcome_thread_seeded':bool(welcome),'thread_created':bool(thread and thread.get('title')=='Smoke thread'),'reply_created':len(replies)>=2}, {'thread_id':tid}))
