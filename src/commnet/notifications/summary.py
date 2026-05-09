from __future__ import annotations
from typing import Any
from commnet.identity.user_store import UserStore
from commnet.mail.store import MailStore
from commnet.hardware.meshtastic_probe import dependency_status as meshtastic_dependency_status, latest_status as meshtastic_latest_status

def build_notification_summary(store, audit=None, cfg: dict | None = None) -> dict[str, Any]:
    cfg = cfg or {}
    us = UserStore(store, audit); ms = MailStore(store, audit)
    users = us.list_users()
    admin_user_ids = [u.get('user_id') for u in users if u.get('role_id') in {'owner', 'admin'}]
    unread_admin_mail = sum(ms.unread_count(uid) for uid in admin_user_ids if uid)
    pending_requests = us.list_permission_requests('pending')
    password_resets = [r for r in us.list_password_resets() if r.get('status') == 'pending']
    default_password_active = us.default_admin_password_active()
    mesh_dep = meshtastic_dependency_status(); mesh_latest = meshtastic_latest_status(store)
    warnings: list[str] = []
    if default_password_active: warnings.append('Default admin password is still active.')
    if not cfg.get('lan_access_enabled'): warnings.append('LAN access is not enabled; phone visitors may not reach this node.')
    if cfg.get('server_host') in ('127.0.0.1', 'localhost'): warnings.append('Server host is localhost-only in config.')
    if not mesh_dep.get('meshtastic_installed'): warnings.append('Meshtastic Python package is not installed.')
    elif mesh_latest.get('state') not in {'connected', 'receive_active'}: warnings.append('Meshtastic is installed but no node has been verified yet.')
    return {'pending_permission_requests': len(pending_requests), 'pending_password_resets': len(password_resets), 'unread_admin_mail': unread_admin_mail, 'default_password_active': default_password_active, 'meshtastic': {**mesh_dep, **mesh_latest}, 'warnings': warnings, 'badge_states': {'users': 'warning' if pending_requests or password_resets else 'ready', 'mail': 'warning' if unread_admin_mail else 'ready', 'devices': 'warning' if any('Meshtastic' in w for w in warnings) else 'ready', 'security': 'warning' if default_password_active else 'ready'}}
