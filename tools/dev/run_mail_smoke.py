from __future__ import annotations

import uuid
from _smoke_common import result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore
from commnet.mail.store import MailStore

paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths, store); us=UserStore(store, audit); ms=MailStore(store, audit)
a='maila_'+uuid.uuid4().hex[:8]; b='mailb_'+uuid.uuid4().hex[:8]
ua=us.create_user(a,'Mail Sender','MailPass123!','user','smoke'); ub=us.create_user(b,'Mail Receiver','MailPass123!','user','smoke')
mid=ms.send(ua,[ub],'Smoke mail','Hello from CommNet mail')
inbox=ms.inbox(ub); unread=ms.unread_count(ub); msg=ms.read(mid, ub); unread2=ms.unread_count(ub)
checks={'sent': bool(mid), 'inbox_seen': any(m['message_id']==mid for m in inbox), 'unread_initial': unread >= 1, 'read_body': msg and msg.get('body')=='Hello from CommNet mail', 'unread_decrements': unread2 <= unread}
raise SystemExit(result('mail_smoke_report.json', checks, {'message_id': mid}))
