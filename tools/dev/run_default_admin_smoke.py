from _smoke_common import runtime, result
from commnet.core.db import SQLiteStore
from commnet.core.audit import AuditLogger
from commnet.identity.user_store import UserStore
paths=runtime(); store=SQLiteStore(paths); store.initialize(); audit=AuditLogger(paths,store); us=UserStore(store,audit); us.ensure_default_admin(); admin=us.get_by_username('admin')
raise SystemExit(result('default_admin_smoke_report.json', {'admin_exists':bool(admin),'admin_is_owner':bool(admin and admin.get('role_id')=='owner'),'default_password_active_detected':us.default_admin_password_active()}, {'admin_user_id': admin.get('user_id') if admin else ''}))
