from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from commnet.identity.auth import (
    AuthInputError,
    hash_password,
    new_session_id,
    validate_display_name,
    validate_hint,
    validate_password,
    validate_username,
    verify_password,
)

ROLE_PERMISSIONS = {
    'owner': ['*'],
    'admin': ['admin.*', 'mail.*', 'share.*', 'portal.*'],
    'trusted_user': ['mail.use', 'portal.view', 'share.approved'],
    'user': ['mail.use', 'portal.view'],
    'guest': ['portal.view', 'requests.create'],
    'retroweb_user': ['portal.retroweb.view'],
    'suspended': [],
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _expiry(hours: int = 12) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


class UserStore:
    def __init__(self, store, audit=None):
        self.store = store
        self.audit = audit
        self.store.initialize()

    def bootstrap_needed(self) -> bool:
        with self.store.connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM auth_credentials WHERE status!='deleted'").fetchone()
        return int(row[0]) == 0


    def ensure_default_admin(self) -> str | None:
        """Create the appliance-style default owner if the admin username is missing."""
        existing = self.get_by_username('admin')
        if existing:
            return None
        user_id = self.create_user('admin', 'CommNet Admin', 'password', 'owner', 'default password is password')
        if self.audit:
            self.audit.write('default_admin_seeded', {'username': 'admin', 'role_id': 'owner'})
        return user_id

    def default_admin_password_active(self) -> bool:
        user = self.get_by_username('admin')
        if not user or user.get('status') != 'active':
            return False
        return verify_password('password', user.get('password_salt',''), user.get('password_hash',''), int(user.get('password_iterations') or 0))

    def admin_user_id(self) -> str:
        user = self.get_by_username('admin')
        return user.get('user_id') if user else 'local_admin'

    def create_user(self, username: str, display_name: str, password: str, role_id: str = 'user', password_hint: str = '', status: str = 'active') -> str:
        username = validate_username(username)
        display_name = validate_display_name(display_name)
        password = validate_password(password)
        password_hint = validate_hint(password_hint, password)
        role_id = role_id if role_id in ROLE_PERMISSIONS else 'user'
        user_id = 'user_' + uuid.uuid4().hex[:12]
        hp = hash_password(password)
        with self.store.connect() as conn:
            try:
                conn.execute('INSERT INTO users_local(user_id, display_name, role_id) VALUES (?, ?, ?)', (user_id, display_name, role_id))
                conn.execute('''INSERT INTO auth_credentials(user_id, username, password_hash, password_salt, password_iterations, password_scheme, password_hint, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                             (user_id, username, hp['hash_hex'], hp['salt_hex'], hp['iterations'], hp['scheme'], password_hint, status))
                conn.commit()
            except sqlite3.IntegrityError as exc:
                raise AuthInputError('Username already exists.') from exc
        if self.audit:
            self.audit.write('local_user_created', {'user_id': user_id, 'username': username, 'role_id': role_id, 'status': status})
        return user_id

    def list_users(self) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute('''SELECT u.user_id, u.display_name, u.role_id, u.created_at, u.updated_at,
                                          c.username, c.password_hint, c.status, c.last_login_at
                                   FROM users_local u JOIN auth_credentials c ON c.user_id=u.user_id
                                   WHERE c.status!='deleted'
                                   ORDER BY u.created_at DESC''').fetchall()
        return [dict(r) for r in rows]

    def get_by_username(self, username: str) -> dict[str, Any] | None:
        username = (username or '').strip().lower()
        with self.store.connect() as conn:
            row = conn.execute('''SELECT u.user_id, u.display_name, u.role_id, c.username, c.password_hash, c.password_salt,
                                         c.password_iterations, c.password_scheme, c.password_hint, c.status, c.last_login_at
                                  FROM users_local u JOIN auth_credentials c ON c.user_id=u.user_id WHERE c.username=?''', (username,)).fetchone()
        return dict(row) if row else None

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute('''SELECT u.user_id, u.display_name, u.role_id, c.username, c.password_hint, c.status, c.last_login_at
                                  FROM users_local u JOIN auth_credentials c ON c.user_id=u.user_id WHERE u.user_id=?''', (user_id,)).fetchone()
        return dict(row) if row else None

    def authenticate(self, username: str, password: str, client_ip: str = '', user_agent: str = '') -> dict[str, Any]:
        user = self.get_by_username(username)
        if not user or user.get('status') != 'active':
            raise AuthInputError('Invalid username/password or inactive account.')
        ok = verify_password(password, user.get('password_salt',''), user.get('password_hash',''), int(user.get('password_iterations') or 0))
        if not ok:
            if self.audit:
                self.audit.write('local_login_failed', {'username': (username or '').strip().lower(), 'client_ip': client_ip})
            raise AuthInputError('Invalid username/password or inactive account.')
        with self.store.connect() as conn:
            conn.execute('UPDATE auth_credentials SET last_login_at=CURRENT_TIMESTAMP WHERE user_id=?', (user['user_id'],))
            conn.commit()
        session = self.create_session(user['user_id'], client_ip, user_agent)
        user_public = self.get_user(user['user_id']) or user
        user_public['session_id'] = session
        if self.audit:
            self.audit.write('local_login_ok', {'user_id': user['user_id'], 'username': user.get('username'), 'client_ip': client_ip})
        return user_public

    def create_session(self, user_id: str, client_ip: str = '', user_agent: str = '') -> str:
        sid = new_session_id()
        with self.store.connect() as conn:
            conn.execute('''INSERT INTO sessions(session_id, user_id, expires_at, client_ip, user_agent_hash)
                            VALUES (?, ?, ?, ?, ?)''', (sid, user_id, _expiry(), client_ip[:80], str(hash(user_agent))[:80]))
            conn.commit()
        return sid

    def get_session_user(self, session_id: str | None) -> dict[str, Any] | None:
        if not session_id:
            return None
        with self.store.connect() as conn:
            row = conn.execute('''SELECT s.session_id, s.expires_at, s.revoked, u.user_id, u.display_name, u.role_id,
                                         c.username, c.status
                                  FROM sessions s JOIN users_local u ON u.user_id=s.user_id
                                  JOIN auth_credentials c ON c.user_id=u.user_id
                                  WHERE s.session_id=?''', (session_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            if data.get('revoked') or data.get('status') != 'active':
                return None
            try:
                exp = datetime.fromisoformat(data.get('expires_at'))
                if exp < datetime.now(timezone.utc):
                    return None
            except Exception:
                return None
            conn.execute('UPDATE sessions SET last_seen_at=CURRENT_TIMESTAMP WHERE session_id=?', (session_id,))
            conn.commit()
        return data

    def revoke_session(self, session_id: str | None) -> None:
        if not session_id:
            return
        with self.store.connect() as conn:
            conn.execute('UPDATE sessions SET revoked=1 WHERE session_id=?', (session_id,))
            conn.commit()

    def set_role(self, user_id: str, role_id: str) -> None:
        if role_id not in ROLE_PERMISSIONS:
            raise AuthInputError('Unknown role.')
        with self.store.connect() as conn:
            conn.execute('UPDATE users_local SET role_id=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=?', (role_id, user_id))
            conn.commit()
        if self.audit:
            self.audit.write('local_user_role_updated', {'user_id': user_id, 'role_id': role_id})

    def reset_password(self, user_id: str, new_password: str, hint: str = '') -> None:
        new_password = validate_password(new_password)
        hint = validate_hint(hint, new_password)
        hp = hash_password(new_password)
        with self.store.connect() as conn:
            conn.execute('''UPDATE auth_credentials SET password_hash=?, password_salt=?, password_iterations=?, password_scheme=?, password_hint=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=?''',
                         (hp['hash_hex'], hp['salt_hex'], hp['iterations'], hp['scheme'], hint, user_id))
            conn.commit()
        if self.audit:
            self.audit.write('local_password_reset_by_admin', {'user_id': user_id})

    def request_password_reset(self, username: str, note: str = '') -> str:
        user = self.get_by_username(username)
        req_id = 'pwreq_' + uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute('INSERT INTO password_reset_requests(request_id, user_id, username, note, status) VALUES (?, ?, ?, ?, ?)',
                         (req_id, user.get('user_id') if user else '', (username or '')[:64], note[:500], 'pending'))
            conn.commit()
        if self.audit:
            self.audit.write('password_reset_requested', {'request_id': req_id, 'username': (username or '')[:64], 'matched_user': bool(user)})
        return req_id

    def list_password_resets(self) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute('SELECT * FROM password_reset_requests ORDER BY created_at DESC LIMIT 100').fetchall()
        return [dict(r) for r in rows]

    def create_permission_request(self, user_id: str, target_type: str, target_id: str, requested_permission: str, reason: str = '') -> str:
        req_id = 'req_' + uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute('''INSERT INTO permission_requests(request_id, user_id, target_type, target_id, requested_permission, reason, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'pending')''',
                         (req_id, user_id, target_type[:40], target_id[:120], requested_permission[:120], reason[:500]))
            conn.commit()
        if self.audit:
            self.audit.write('permission_request_created', {'request_id': req_id, 'user_id': user_id, 'target_type': target_type, 'target_id': target_id})
        return req_id

    def list_permission_requests(self, status: str | None = None) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            if status:
                rows = conn.execute('''SELECT pr.*, u.display_name, c.username FROM permission_requests pr
                                       LEFT JOIN users_local u ON u.user_id=pr.user_id
                                       LEFT JOIN auth_credentials c ON c.user_id=pr.user_id
                                       WHERE pr.status=? ORDER BY pr.created_at DESC''', (status,)).fetchall()
            else:
                rows = conn.execute('''SELECT pr.*, u.display_name, c.username FROM permission_requests pr
                                       LEFT JOIN users_local u ON u.user_id=pr.user_id
                                       LEFT JOIN auth_credentials c ON c.user_id=pr.user_id
                                       ORDER BY pr.created_at DESC LIMIT 200''').fetchall()
        return [dict(r) for r in rows]

    def resolve_permission_request(self, request_id: str, status: str, admin_user_id: str = 'local_admin', response: str = '') -> None:
        if status not in {'approved', 'denied', 'needs_info', 'cancelled'}:
            raise AuthInputError('Invalid request status.')
        with self.store.connect() as conn:
            req = conn.execute('SELECT * FROM permission_requests WHERE request_id=?', (request_id,)).fetchone()
            if not req:
                raise AuthInputError('Request not found.')
            conn.execute('''UPDATE permission_requests SET status=?, admin_response=?, resolved_by=?, resolved_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
                            WHERE request_id=?''', (status, response[:500], admin_user_id, request_id))
            if status == 'approved':
                conn.execute('''INSERT INTO permission_grants(grant_id, user_id, permission, scope_type, scope_id, granted_by)
                                VALUES (?, ?, ?, ?, ?, ?)''',
                             ('grant_' + uuid.uuid4().hex[:12], req['user_id'], req['requested_permission'], req['target_type'], req['target_id'], admin_user_id))
            conn.commit()
        if self.audit:
            self.audit.write('permission_request_resolved', {'request_id': request_id, 'status': status, 'admin_user_id': admin_user_id})

    def grants_for_user(self, user_id: str) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute('SELECT * FROM permission_grants WHERE user_id=? AND revoked_at IS NULL ORDER BY created_at DESC', (user_id,)).fetchall()
        return [dict(r) for r in rows]

    def user_has(self, user: dict[str, Any] | None, permission: str, scope_id: str = '') -> bool:
        if not user:
            return False
        role = user.get('role_id') or 'guest'
        perms = ROLE_PERMISSIONS.get(role, [])
        if '*' in perms:
            return True
        if permission in perms:
            return True
        for p in perms:
            if p.endswith('.*') and permission.startswith(p[:-1]):
                return True
        for grant in self.grants_for_user(user.get('user_id','')):
            gp = grant.get('permission') or ''
            if gp == permission or (gp.endswith('.*') and permission.startswith(gp[:-1])):
                if not scope_id or not grant.get('scope_id') or grant.get('scope_id') == scope_id:
                    return True
        return False


    def update_display_name(self, user_id: str, display_name: str) -> None:
        display_name = validate_display_name(display_name)
        with self.store.connect() as conn:
            conn.execute('UPDATE users_local SET display_name=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=?', (display_name, user_id))
            conn.commit()
        if self.audit:
            self.audit.write('local_user_profile_updated', {'user_id': user_id, 'field': 'display_name'})

    def profile_for_user(self, user_id: str) -> dict[str, Any]:
        with self.store.connect() as conn:
            row = conn.execute('SELECT * FROM user_profiles WHERE user_id=?', (user_id,)).fetchone()
        if row:
            return dict(row)
        return {'user_id': user_id, 'about': '', 'icon_kind': 'blank', 'icon_json': '{}'}

    def update_profile(self, user_id: str, about: str = '') -> None:
        about = (about or '')[:500]
        with self.store.connect() as conn:
            conn.execute('''INSERT INTO user_profiles(user_id, about) VALUES (?, ?)
                            ON CONFLICT(user_id) DO UPDATE SET about=excluded.about, updated_at=CURRENT_TIMESTAMP''',
                         (user_id, about))
            conn.commit()
        if self.audit:
            self.audit.write('local_user_profile_updated', {'user_id': user_id, 'field': 'about'})

    def set_icon(self, user_id: str, icon_kind: str, icon_json: str = '{}') -> None:
        icon_kind = icon_kind if icon_kind in {'blank', 'generated', 'uploaded'} else 'blank'
        icon_json = (icon_json or '{}')[:2000]
        with self.store.connect() as conn:
            conn.execute('''INSERT INTO user_profiles(user_id, icon_kind, icon_json) VALUES (?, ?, ?)
                            ON CONFLICT(user_id) DO UPDATE SET icon_kind=excluded.icon_kind, icon_json=excluded.icon_json, updated_at=CURRENT_TIMESTAMP''',
                         (user_id, icon_kind, icon_json))
            conn.commit()
        if self.audit:
            self.audit.write('local_user_icon_updated', {'user_id': user_id, 'icon_kind': icon_kind})
