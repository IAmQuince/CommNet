from __future__ import annotations

import uuid
from _smoke_common import result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore

paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths, store); us=UserStore(store, audit)
name='perm_'+uuid.uuid4().hex[:8]
uid=us.create_user(name, 'Perm User', 'PermPass123!', 'guest', 'smoke')
req=us.create_permission_request(uid, 'portal', 'retroweb', 'portal.retroweb.view', 'smoke request')
pending=[r for r in us.list_permission_requests('pending') if r['request_id']==req]
us.resolve_permission_request(req, 'approved', 'local_admin', 'ok')
grants=us.grants_for_user(uid)
checks={'request_created': bool(req), 'pending_visible': len(pending)==1, 'grant_created': any(g['permission']=='portal.retroweb.view' for g in grants), 'user_has_grant': us.user_has({'user_id': uid, 'role_id': 'guest'}, 'portal.retroweb.view', 'retroweb')}
raise SystemExit(result('permission_request_report.json', checks, {'request_id': req, 'user_id': uid}))
