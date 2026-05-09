
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from commnet.share.models import PERMISSION_PROFILES
from commnet.share.path_guard import validate_share_root


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _code_hash(code: str) -> str:
    return hashlib.sha256(code.encode('utf-8')).hexdigest()


class ShareStore:
    def __init__(self, store, audit=None, package_root: Path | None = None):
        self.store = store
        self.audit = audit
        self.package_root = Path(package_root).resolve() if package_root else None
        self.ensure_tables()

    def ensure_tables(self) -> None:
        self.store.initialize()
        with self.store.connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS share_roots (
                share_id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                root_path TEXT NOT NULL,
                virtual_name TEXT NOT NULL UNIQUE,
                visibility_mode TEXT NOT NULL DEFAULT 'private',
                permission_profile TEXT NOT NULL DEFAULT 'list_and_download',
                allow_list INTEGER NOT NULL DEFAULT 1,
                allow_download INTEGER NOT NULL DEFAULT 1,
                allow_upload INTEGER NOT NULL DEFAULT 0,
                allow_delete INTEGER NOT NULL DEFAULT 0,
                allow_overwrite INTEGER NOT NULL DEFAULT 0,
                upload_subfolder TEXT NOT NULL DEFAULT '_CommNet_Inbox',
                require_access_code INTEGER NOT NULL DEFAULT 1,
                enabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                visibility_behavior TEXT NOT NULL DEFAULT 'download',
                allow_preview INTEGER NOT NULL DEFAULT 0,
                preview_policy_json TEXT NOT NULL DEFAULT '{}'
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS share_access_events (
                event_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                remote_addr TEXT NOT NULL DEFAULT '',
                share_id TEXT,
                virtual_path TEXT NOT NULL DEFAULT '',
                action TEXT NOT NULL,
                result TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT ''
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS share_access_codes (
                code_id TEXT PRIMARY KEY,
                code_hash TEXT NOT NULL,
                label TEXT NOT NULL DEFAULT 'LAN visitor code',
                enabled INTEGER NOT NULL DEFAULT 1,
                expires_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_used_at TEXT
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS share_downloads (
                download_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                remote_addr TEXT NOT NULL DEFAULT '',
                share_id TEXT NOT NULL,
                virtual_path TEXT NOT NULL,
                size_bytes INTEGER NOT NULL DEFAULT 0,
                result TEXT NOT NULL
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS share_uploads (
                upload_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                remote_addr TEXT NOT NULL DEFAULT '',
                share_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                size_bytes INTEGER NOT NULL DEFAULT 0,
                result TEXT NOT NULL,
                saved_path TEXT NOT NULL DEFAULT ''
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS lan_access_events (
                event_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                remote_addr TEXT NOT NULL DEFAULT '',
                path TEXT NOT NULL DEFAULT '',
                result TEXT NOT NULL DEFAULT '',
                reason TEXT NOT NULL DEFAULT ''
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS quick_setup_runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                selected_mode TEXT NOT NULL,
                lan_enabled INTEGER NOT NULL DEFAULT 0,
                selected_share_count INTEGER NOT NULL DEFAULT 0,
                result TEXT NOT NULL
            )""")
            for name, ddl in [
                ('visibility_behavior', "TEXT NOT NULL DEFAULT 'download'"),
                ('allow_preview', "INTEGER NOT NULL DEFAULT 0"),
                ('preview_policy_json', "TEXT NOT NULL DEFAULT '{}'"),
            ]:
                cols = {row[1] for row in conn.execute('PRAGMA table_info(share_roots)').fetchall()}
                if name not in cols:
                    conn.execute(f'ALTER TABLE share_roots ADD COLUMN {name} {ddl}')
            conn.commit()

    def add_share(self, label: str, root_path: str, virtual_name: str, visibility_mode: str = 'private', permission_profile: str = 'list_and_download', enabled: bool = False, require_access_code: bool = True, visibility_behavior: str | None = None, allow_preview: bool | None = None) -> str:
        ok, reason = validate_share_root(root_path, self.package_root)
        if not ok:
            raise ValueError(reason)
        virtual_name = ''.join(c for c in virtual_name.strip().replace(' ', '_') if c.isalnum() or c in ('_', '-', '.')) or 'Share'
        perms = dict(PERMISSION_PROFILES.get(permission_profile, PERMISSION_PROFILES['list_and_download']))
        behavior = visibility_behavior or {
            'private': 'admin_only',
            'list_only': 'list_only',
            'list_and_download': 'download',
            'dropbox_upload_only': 'upload_inbox',
            'list_download_upload_inbox': 'download',
            'advanced_custom': 'download',
            'preview_only': 'preview_only',
        }.get(permission_profile, 'download')
        if behavior == 'invisible':
            perms.update({'allow_list': False, 'allow_download': False, 'allow_upload': False})
        elif behavior == 'count_only':
            perms.update({'allow_list': False, 'allow_download': False, 'allow_upload': False})
        elif behavior == 'list_only':
            perms.update({'allow_list': True, 'allow_download': False, 'allow_upload': False})
        elif behavior == 'preview_only':
            perms.update({'allow_list': True, 'allow_download': False})
        elif behavior == 'download':
            perms.update({'allow_list': True, 'allow_download': True})
        elif behavior == 'upload_inbox':
            perms.update({'allow_upload': True})
        elif behavior == 'admin_only':
            visibility_mode = 'private'
        preview_flag = bool(allow_preview if allow_preview is not None else behavior in ('preview_only', 'download'))
        share_id = 'share_' + uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute("""INSERT INTO share_roots(share_id, label, root_path, virtual_name, visibility_mode, permission_profile, allow_list, allow_download, allow_upload, allow_delete, allow_overwrite, require_access_code, enabled, visibility_behavior, allow_preview, preview_policy_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (share_id, label.strip(), str(Path(root_path).expanduser().resolve()), virtual_name, visibility_mode, permission_profile,
                 int(perms.get('allow_list')), int(perms.get('allow_download')), int(perms.get('allow_upload')), int(perms.get('allow_delete')), int(perms.get('allow_overwrite')), int(require_access_code), int(enabled), behavior, int(preview_flag), json.dumps({'safe_preview_only': True}, sort_keys=True)))
            conn.commit()
        if self.audit:
            self.audit.write('share_root_added', {'share_id': share_id, 'label': label, 'visibility': visibility_mode, 'permission_profile': permission_profile, 'enabled': enabled})
        return share_id

    def delete_share(self, share_id: str) -> None:
        with self.store.connect() as conn:
            conn.execute('DELETE FROM share_roots WHERE share_id=?', (share_id,))
            conn.commit()
        if self.audit:
            self.audit.write('share_root_deleted', {'share_id': share_id})

    def list_shares(self, visitor_visible: bool = False) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            if visitor_visible:
                rows = conn.execute("SELECT * FROM share_roots WHERE enabled=1 AND visibility_mode IN ('lan_visible','community_visible') ORDER BY label").fetchall()
            else:
                rows = conn.execute('SELECT * FROM share_roots ORDER BY updated_at DESC, created_at DESC').fetchall()
        return [dict(r) for r in rows]

    def get_share(self, share_id: str) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            row = conn.execute('SELECT * FROM share_roots WHERE share_id=? OR virtual_name=?', (share_id, share_id)).fetchone()
        return dict(row) if row else None

    def update_share_policy(self, share_id: str, visibility_mode: str, permission_profile: str, visibility_behavior: str, enabled: bool, require_access_code: bool, allow_preview: bool) -> None:
        perms = dict(PERMISSION_PROFILES.get(permission_profile, PERMISSION_PROFILES['list_and_download']))
        if visibility_behavior == 'invisible':
            perms.update({'allow_list': False, 'allow_download': False, 'allow_upload': False})
        elif visibility_behavior == 'count_only':
            perms.update({'allow_list': False, 'allow_download': False, 'allow_upload': False})
        elif visibility_behavior == 'list_only':
            perms.update({'allow_list': True, 'allow_download': False, 'allow_upload': False})
        elif visibility_behavior == 'preview_only':
            perms.update({'allow_list': True, 'allow_download': False})
        elif visibility_behavior == 'download':
            perms.update({'allow_list': True, 'allow_download': True})
        elif visibility_behavior == 'upload_inbox':
            perms.update({'allow_upload': True})
        elif visibility_behavior == 'admin_only':
            visibility_mode = 'private'
            perms.update({'allow_list': False, 'allow_download': False, 'allow_upload': False})
        with self.store.connect() as conn:
            conn.execute('''UPDATE share_roots SET visibility_mode=?, permission_profile=?, visibility_behavior=?, allow_list=?, allow_download=?, allow_upload=?, enabled=?, require_access_code=?, allow_preview=?, updated_at=CURRENT_TIMESTAMP WHERE share_id=?''',
                         (visibility_mode, permission_profile, visibility_behavior, int(perms.get('allow_list')), int(perms.get('allow_download')), int(perms.get('allow_upload')), int(enabled), int(require_access_code), int(allow_preview), share_id))
            conn.commit()
        if self.audit:
            self.audit.write('share_policy_updated', {'share_id': share_id, 'visibility': visibility_mode, 'permission_profile': permission_profile, 'behavior': visibility_behavior, 'enabled': enabled})

    def share_count(self, share: dict[str, Any]) -> dict[str, int]:
        root = Path(share['root_path'])
        files = 0
        folders = 0
        for child in root.rglob('*'):
            try:
                if child.name.startswith('.'):
                    continue
                if child.is_dir():
                    folders += 1
                elif child.is_file():
                    files += 1
            except OSError:
                continue
            if files + folders > 10000:
                break
        return {'files': files, 'folders': folders, 'truncated': int(files + folders > 10000)}

    def log_access(self, remote_addr: str, action: str, result: str, share_id: str | None = None, virtual_path: str = '', reason: str = '') -> None:
        with self.store.connect() as conn:
            conn.execute('INSERT INTO share_access_events(event_id, remote_addr, share_id, virtual_path, action, result, reason) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         ('share_evt_' + uuid.uuid4().hex[:12], remote_addr, share_id, virtual_path, action, result, reason[:500]))
            conn.commit()

    def log_lan(self, remote_addr: str, path: str, result: str, reason: str = '') -> None:
        with self.store.connect() as conn:
            conn.execute('INSERT INTO lan_access_events(event_id, remote_addr, path, result, reason) VALUES (?, ?, ?, ?, ?)',
                         ('lan_evt_' + uuid.uuid4().hex[:12], remote_addr, path[:260], result, reason[:500]))
            conn.commit()

    def set_access_code(self, code: str, label: str = 'LAN visitor code') -> str:
        if not (4 <= len(code) <= 64):
            raise ValueError('Access code must be 4 to 64 characters.')
        code_id = 'code_' + uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute('UPDATE share_access_codes SET enabled=0')
            conn.execute('INSERT INTO share_access_codes(code_id, code_hash, label, enabled) VALUES (?, ?, ?, 1)', (code_id, _code_hash(code), label))
            conn.commit()
        if self.audit:
            self.audit.write('share_access_code_created', {'code_id': code_id, 'label': label})
        return code_id

    def verify_code(self, code: str) -> bool:
        if not code:
            return False
        h = _code_hash(code)
        with self.store.connect() as conn:
            row = conn.execute('SELECT code_id FROM share_access_codes WHERE code_hash=? AND enabled=1', (h,)).fetchone()
            if row:
                conn.execute('UPDATE share_access_codes SET last_used_at=CURRENT_TIMESTAMP WHERE code_id=?', (row['code_id'],))
                conn.commit()
                return True
        return False

    def access_code_count(self) -> int:
        with self.store.connect() as conn:
            return int(conn.execute('SELECT COUNT(*) FROM share_access_codes WHERE enabled=1').fetchone()[0])

    def record_quick_setup(self, selected_mode: str, lan_enabled: bool, selected_share_count: int, result: str) -> None:
        with self.store.connect() as conn:
            conn.execute('INSERT INTO quick_setup_runs(run_id, selected_mode, lan_enabled, selected_share_count, result) VALUES (?, ?, ?, ?, ?)',
                         ('qs_' + uuid.uuid4().hex[:12], selected_mode, int(lan_enabled), selected_share_count, result))
            conn.commit()

    def recent_access(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute('SELECT * FROM share_access_events ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [dict(r) for r in rows]

    def summary(self) -> dict[str, Any]:
        shares = self.list_shares(False)
        return {
            'share_count': len(shares),
            'enabled_share_count': sum(1 for s in shares if s.get('enabled')),
            'lan_visible_share_count': sum(1 for s in shares if s.get('enabled') and s.get('visibility_mode') == 'lan_visible'),
            'upload_enabled_share_count': sum(1 for s in shares if s.get('enabled') and s.get('allow_upload')),
            'access_code_count': self.access_code_count(),
            'shares': [{k: v for k, v in s.items() if k not in ('root_path',)} | {'physical_path_redacted': True} for s in shares],
        }
