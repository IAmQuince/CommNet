from __future__ import annotations

import uuid
from _smoke_common import result, runtime
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore

paths = runtime(); store = SQLiteStore(paths); store.initialize(); audit = AuditLogger(paths, store); us = UserStore(store, audit)
name = 'smoke_' + uuid.uuid4().hex[:8]
uid = us.create_user(name, 'Smoke User', 'SmokePass123!', 'guest', 'temporary smoke account')
user = us.authenticate(name, 'SmokePass123!', '127.0.0.1', 'smoke')
sess_user = us.get_session_user(user['session_id'])
checks = {'created': bool(uid), 'authenticated': user.get('user_id') == uid, 'session_lookup': bool(sess_user and sess_user.get('user_id') == uid), 'role_guest': sess_user.get('role_id') == 'guest'}
raise SystemExit(result('auth_smoke_report.json', checks, {'user_id': uid, 'username': name}))
