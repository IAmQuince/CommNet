from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Any

SCHEMA_VERSION = '10'

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS schema_meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS config_kv (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS config_snapshots (
        snapshot_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        reason TEXT NOT NULL,
        filename TEXT NOT NULL,
        config_hash TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS config_changes (
        change_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        actor TEXT NOT NULL,
        field_path TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT,
        reason TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT NOT NULL,
        details_json TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        device_type TEXT NOT NULL,
        trust_state TEXT NOT NULL DEFAULT 'known',
        notes TEXT NOT NULL DEFAULT '',
        desired_transports_json TEXT NOT NULL DEFAULT '[]',
        details_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS file_roots (
        root_id TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        root_path TEXT NOT NULL,
        default_visibility TEXT NOT NULL DEFAULT 'private',
        scan_enabled INTEGER NOT NULL DEFAULT 0,
        include_subfolders INTEGER NOT NULL DEFAULT 1,
        review_required INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS services (
        service_id TEXT PRIMARY KEY,
        enabled INTEGER NOT NULL DEFAULT 0,
        visible_in_portal INTEGER NOT NULL DEFAULT 0,
        requires_review INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'available_disabled',
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS policy_rules (
        rule_id TEXT PRIMARY KEY,
        rule_type TEXT NOT NULL,
        rule_json TEXT NOT NULL,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS roles (
        role_id TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        permissions_json TEXT NOT NULL DEFAULT '[]',
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS users_local (
        user_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        role_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",

    """CREATE TABLE IF NOT EXISTS auth_credentials (
        user_id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        password_iterations INTEGER NOT NULL,
        password_scheme TEXT NOT NULL DEFAULT 'pbkdf2_sha256',
        password_hint TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT NOT NULL,
        last_seen_at TEXT,
        client_ip TEXT NOT NULL DEFAULT '',
        user_agent_hash TEXT NOT NULL DEFAULT '',
        revoked INTEGER NOT NULL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS permission_grants (
        grant_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        permission TEXT NOT NULL,
        scope_type TEXT NOT NULL DEFAULT '',
        scope_id TEXT NOT NULL DEFAULT '',
        granted_by TEXT NOT NULL DEFAULT 'local_admin',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT,
        revoked_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS permission_requests (
        request_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id TEXT NOT NULL DEFAULT '',
        requested_permission TEXT NOT NULL,
        reason TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'pending',
        admin_response TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        resolved_by TEXT NOT NULL DEFAULT '',
        resolved_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS password_reset_requests (
        request_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL DEFAULT '',
        username TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'pending',
        admin_response TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        resolved_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS mail_messages (
        message_id TEXT PRIMARY KEY,
        sender_user_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        system_message INTEGER NOT NULL DEFAULT 0,
        broadcast INTEGER NOT NULL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS mail_recipients (
        message_id TEXT NOT NULL,
        recipient_user_id TEXT NOT NULL,
        read_at TEXT,
        deleted_at TEXT,
        folder_state TEXT NOT NULL DEFAULT 'inbox',
        PRIMARY KEY (message_id, recipient_user_id)
    )""",
    """CREATE TABLE IF NOT EXISTS bbs_posts (
        post_id TEXT PRIMARY KEY,
        author_user_id TEXT NOT NULL DEFAULT '',
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'published',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS bbs_boards (
        board_id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
        sort_order INTEGER NOT NULL DEFAULT 100, status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS bbs_threads (
        thread_id TEXT PRIMARY KEY, board_id TEXT NOT NULL, title TEXT NOT NULL, author_user_id TEXT NOT NULL DEFAULT '',
        pinned INTEGER NOT NULL DEFAULT 0, locked INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'published', seed_key TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS bbs_replies (
        reply_id TEXT PRIMARY KEY, thread_id TEXT NOT NULL, author_user_id TEXT NOT NULL DEFAULT '', body TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'published', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS retroweb_profiles (
        user_id TEXT PRIMARY KEY, handle TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL, about TEXT NOT NULL DEFAULT '', icon_json TEXT NOT NULL DEFAULT '{}',
        status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        about TEXT NOT NULL DEFAULT '',
        icon_kind TEXT NOT NULL DEFAULT 'blank',
        icon_json TEXT NOT NULL DEFAULT '{}',
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS retroweb_posts (
        post_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, body TEXT NOT NULL, visibility TEXT NOT NULL DEFAULT 'retroweb', status TEXT NOT NULL DEFAULT 'published',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS retroweb_comments (
        comment_id TEXT PRIMARY KEY, post_id TEXT NOT NULL, user_id TEXT NOT NULL, body TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'published',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS retroweb_follows (
        follower_user_id TEXT NOT NULL, following_user_id TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (follower_user_id, following_user_id)
    )""",
    """CREATE TABLE IF NOT EXISTS meshtastic_events (
        event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, state TEXT NOT NULL, details_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS transport_adapters (
        adapter_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        status TEXT NOT NULL,
        details_json TEXT NOT NULL DEFAULT '{}',
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS peers (
        peer_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        base_url TEXT NOT NULL UNIQUE,
        trust_state TEXT NOT NULL DEFAULT 'known',
        visibility_scope TEXT NOT NULL DEFAULT 'manual',
        notes TEXT NOT NULL DEFAULT '',
        last_seen_at TEXT,
        last_status TEXT NOT NULL DEFAULT 'not_tested',
        last_handshake_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS peer_handshakes (
        handshake_id TEXT PRIMARY KEY,
        peer_id TEXT NOT NULL,
        attempted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        result TEXT NOT NULL,
        details_json TEXT NOT NULL DEFAULT '{}'
    )""",
    """CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        sender_node_id TEXT NOT NULL DEFAULT '',
        target TEXT NOT NULL DEFAULT 'self',
        payload_class TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'normal',
        privacy_class TEXT NOT NULL DEFAULT 'local',
        latency_class TEXT NOT NULL DEFAULT 'normal',
        payload_json TEXT NOT NULL DEFAULT '{}',
        payload_size INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'created',
        expires_at TEXT,
        attempt_count INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        destination TEXT NOT NULL DEFAULT '',
        body TEXT NOT NULL DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS route_decisions (
        decision_id TEXT PRIMARY KEY,
        message_id TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        chosen_adapter TEXT,
        score_json TEXT NOT NULL DEFAULT '{}',
        rejected_json TEXT NOT NULL DEFAULT '[]',
        reason TEXT NOT NULL DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS delivery_attempts (
        attempt_id TEXT PRIMARY KEY,
        message_id TEXT NOT NULL,
        adapter_id TEXT NOT NULL,
        peer_id TEXT,
        started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        finished_at TEXT,
        result TEXT NOT NULL,
        success INTEGER NOT NULL DEFAULT 0,
        error TEXT NOT NULL DEFAULT '',
        latency_ms INTEGER,
        result_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS transport_dependencies (
        dependency_id TEXT PRIMARY KEY,
        import_name TEXT NOT NULL,
        package_name TEXT NOT NULL,
        installed INTEGER NOT NULL DEFAULT 0,
        version TEXT,
        checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        notes TEXT NOT NULL DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS adapter_events (
        event_id TEXT PRIMARY KEY,
        adapter_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        details_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS network_events (
        event_id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        details_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS runtime_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT NOT NULL,
        details_json TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS support_exports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        path TEXT NOT NULL,
        details_json TEXT NOT NULL DEFAULT '{}'
    )""",

    """CREATE TABLE IF NOT EXISTS node_identity (
        node_id TEXT PRIMARY KEY,
        commnet_user_id TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS peer_invites (
        invite_id TEXT PRIMARY KEY,
        commnet_user_id TEXT NOT NULL,
        base_url TEXT NOT NULL,
        access_code_hash TEXT,
        expires_at TEXT,
        enabled INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS hardware_devices (
        device_id TEXT PRIMARY KEY,
        device_type TEXT NOT NULL,
        display_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'declared',
        details_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS serial_devices (
        serial_id TEXT PRIMARY KEY,
        port TEXT NOT NULL,
        baud INTEGER NOT NULL DEFAULT 115200,
        device_hint TEXT NOT NULL DEFAULT '',
        last_status TEXT NOT NULL DEFAULT 'not_tested',
        details_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS catena_events (
        event_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        port TEXT NOT NULL DEFAULT '',
        direction TEXT NOT NULL,
        line_text_redacted TEXT NOT NULL DEFAULT '',
        parsed_type TEXT NOT NULL DEFAULT '',
        result TEXT NOT NULL DEFAULT '',
        error TEXT NOT NULL DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS catena_messages (
        message_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        payload_class TEXT NOT NULL,
        body_preview TEXT NOT NULL DEFAULT '',
        serial_status TEXT NOT NULL DEFAULT '',
        rf_status TEXT NOT NULL DEFAULT 'not_proven',
        remote_ack_status TEXT NOT NULL DEFAULT 'not_received',
        details_json TEXT NOT NULL DEFAULT '{}'
    )""",
    """CREATE TABLE IF NOT EXISTS network_paths (
        path_id TEXT PRIMARY KEY,
        adapter_name TEXT NOT NULL,
        ipv4_address TEXT NOT NULL DEFAULT '',
        subnet_mask TEXT NOT NULL DEFAULT '',
        gateway TEXT NOT NULL DEFAULT '',
        dns_suffix TEXT NOT NULL DEFAULT '',
        classification TEXT NOT NULL DEFAULT '',
        recommendation_score INTEGER NOT NULL DEFAULT 0,
        reason TEXT NOT NULL DEFAULT '',
        suggested_url TEXT NOT NULL DEFAULT '',
        source TEXT NOT NULL DEFAULT '',
        last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS selected_network_path (
        selected_id TEXT PRIMARY KEY,
        path_id TEXT NOT NULL,
        selected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        selected_by TEXT NOT NULL DEFAULT 'local_admin',
        url_base TEXT NOT NULL DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS nav_events (
        event_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        route TEXT NOT NULL,
        event_type TEXT NOT NULL,
        details_json TEXT NOT NULL DEFAULT '{}'
    )""",
]


class SQLiteStore:
    def __init__(self, paths):
        self.paths = paths
        self.path = paths.db / 'commnet.sqlite'

    def connect(self) -> sqlite3.Connection:
        self.paths.ensure_all()
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        self.paths.ensure_all()
        with self.connect() as conn:
            for stmt in SCHEMA:
                conn.execute(stmt)
            self._migrate(conn)
            conn.execute("INSERT OR REPLACE INTO schema_meta(key, value, updated_at) VALUES ('schema_version', ?, CURRENT_TIMESTAMP)", (SCHEMA_VERSION,))
            conn.commit()

    def _columns(self, conn: sqlite3.Connection, table: str) -> set[str]:
        return {row[1] for row in conn.execute(f'PRAGMA table_info({table})').fetchall()}

    def _add_column(self, conn: sqlite3.Connection, table: str, name: str, ddl: str) -> None:
        if name not in self._columns(conn, table):
            conn.execute(f'ALTER TABLE {table} ADD COLUMN {name} {ddl}')

    def _migrate(self, conn: sqlite3.Connection) -> None:
        self._add_column(conn, 'devices', 'notes', "TEXT NOT NULL DEFAULT ''")
        self._add_column(conn, 'devices', 'desired_transports_json', "TEXT NOT NULL DEFAULT '[]'")
        self._add_column(conn, 'devices', 'updated_at', "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")
        self._add_column(conn, 'devices', 'last_status', "TEXT NOT NULL DEFAULT 'configured'")
        self._add_column(conn, 'devices', 'last_tested_at', "TEXT")
        self._add_column(conn, 'devices', 'last_test_result_json', "TEXT NOT NULL DEFAULT '{}'")
        # Share UX v8 columns are idempotent because older databases may already have share_roots.
        try:
            self._add_column(conn, 'share_roots', 'visibility_behavior', "TEXT NOT NULL DEFAULT 'download'")
            self._add_column(conn, 'share_roots', 'allow_preview', "INTEGER NOT NULL DEFAULT 0")
            self._add_column(conn, 'share_roots', 'preview_policy_json', "TEXT NOT NULL DEFAULT '{}'")
        except sqlite3.Error:
            # share_roots is created lazily by ShareStore in older builds.
            pass
        # Messages table existed in v2; add v3 columns idempotently.
        for name, ddl in [
            ('created_at', "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"), ('sender_node_id', "TEXT NOT NULL DEFAULT ''"),
            ('target', "TEXT NOT NULL DEFAULT 'self'"), ('priority', "TEXT NOT NULL DEFAULT 'normal'"),
            ('privacy_class', "TEXT NOT NULL DEFAULT 'local'"), ('latency_class', "TEXT NOT NULL DEFAULT 'normal'"),
            ('payload_json', "TEXT NOT NULL DEFAULT '{}'"), ('payload_size', "INTEGER NOT NULL DEFAULT 0"),
            ('expires_at', "TEXT"), ('attempt_count', "INTEGER NOT NULL DEFAULT 0"),
            ('updated_at', "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"), ('destination', "TEXT NOT NULL DEFAULT ''"), ('body', "TEXT NOT NULL DEFAULT ''")]:
            self._add_column(conn, 'messages', name, ddl)
        for name, ddl in [('attempt_id', "TEXT"), ('peer_id', "TEXT"), ('started_at', "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"),
                          ('finished_at', "TEXT"), ('result', "TEXT NOT NULL DEFAULT ''"), ('error', "TEXT NOT NULL DEFAULT ''"),
                          ('latency_ms', "INTEGER"), ('created_at', "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")]:
            self._add_column(conn, 'delivery_attempts', name, ddl)

    def integrity_check(self) -> str:
        self.initialize()
        with self.connect() as conn:
            row = conn.execute('PRAGMA integrity_check').fetchone()
            return str(row[0]) if row else 'no_result'

    def insert_audit(self, event_type: str, details: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute('INSERT INTO audit_events(event_type, details_json) VALUES (?, ?)', (event_type, json.dumps(details, sort_keys=True)))
            conn.commit()

    def audit_recent(self, limit: int = 100) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute('SELECT id, ts, event_type, details_json FROM audit_events ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        out = []
        for r in rows:
            item = dict(r)
            try: item['details'] = json.loads(item.pop('details_json'))
            except Exception: item['details'] = item.get('details_json')
            out.append(item)
        return out

    def upsert_adapter_status(self, adapter_id: str, display_name: str, status: str, details: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute("""INSERT INTO transport_adapters(adapter_id, display_name, status, details_json)
                   VALUES (?, ?, ?, ?) ON CONFLICT(adapter_id) DO UPDATE SET display_name=excluded.display_name,
                   status=excluded.status, details_json=excluded.details_json, updated_at=CURRENT_TIMESTAMP""",
                (adapter_id, display_name, status, json.dumps(details, sort_keys=True)))
            conn.commit()

    def insert_message(self, message) -> None:
        payload = getattr(message, 'payload_json', {'body': getattr(message, 'body', '')})
        body = getattr(message, 'body', '')
        dest = getattr(message, 'destination', getattr(message, 'target', 'self'))
        with self.connect() as conn:
            conn.execute("""INSERT OR REPLACE INTO messages(message_id, sender_node_id, target, payload_class, priority, privacy_class,
                   latency_class, payload_json, payload_size, status, destination, body, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (message.message_id, getattr(message,'sender_node_id',''), getattr(message,'target',dest), message.payload_class,
                 getattr(message,'priority','normal'), getattr(message,'privacy_class','local'), getattr(message,'latency_class','normal'),
                 json.dumps(payload, sort_keys=True), int(getattr(message,'payload_size',len(str(body)))), getattr(message,'status','created'), dest, body))
            conn.commit()

    def update_message_status(self, message_id: str, status: str) -> None:
        with self.connect() as conn:
            conn.execute('UPDATE messages SET status=?, updated_at=CURRENT_TIMESTAMP WHERE message_id=?', (status, message_id))
            conn.commit()

    def messages_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute('SELECT * FROM messages ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [dict(r) for r in rows]

    def insert_route_decision(self, message_id: str, chosen_adapter: str | None, score: dict[str, Any], rejected: list[dict[str, Any]], reason: str) -> str:
        decision_id = 'route_' + uuid.uuid4().hex[:12]
        with self.connect() as conn:
            conn.execute('INSERT INTO route_decisions(decision_id, message_id, chosen_adapter, score_json, rejected_json, reason) VALUES (?, ?, ?, ?, ?, ?)',
                         (decision_id, message_id, chosen_adapter, json.dumps(score, sort_keys=True), json.dumps(rejected, sort_keys=True), reason))
            conn.commit()
        return decision_id

    def route_decisions_recent(self, limit: int = 25) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute('SELECT * FROM route_decisions ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        out=[]
        for r in rows:
            d=dict(r)
            for k in ('score_json','rejected_json'):
                try: d[k[:-5] if k.endswith('_json') else k] = json.loads(d.get(k) or '{}')
                except Exception: pass
            out.append(d)
        return out

    def insert_delivery_attempt(self, message_id: str, adapter_id: str, success: bool, result: dict[str, Any], peer_id: str | None = None, latency_ms: int | None = None) -> str:
        attempt_id = 'attempt_' + uuid.uuid4().hex[:12]
        status = 'delivered' if success else 'failed'
        error = '' if success else str(result.get('detail') or result.get('error') or '')[:500]
        with self.connect() as conn:
            conn.execute("""INSERT INTO delivery_attempts(attempt_id, message_id, adapter_id, peer_id, finished_at, result, success, error, latency_ms, result_json)
                          VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)""",
                         (attempt_id, message_id, adapter_id, peer_id, status, 1 if success else 0, error, latency_ms, json.dumps(result, sort_keys=True)))
            conn.commit()
        return attempt_id

    def delivery_attempts_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute('SELECT * FROM delivery_attempts ORDER BY created_at DESC, started_at DESC LIMIT ?', (limit,)).fetchall()
        return [dict(r) for r in rows]

    def record_dependency(self, import_name: str, package_name: str, installed: bool, version: str | None, notes: str = '') -> None:
        with self.connect() as conn:
            conn.execute("""INSERT INTO transport_dependencies(dependency_id, import_name, package_name, installed, version, notes)
                          VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(dependency_id) DO UPDATE SET installed=excluded.installed,
                          version=excluded.version, checked_at=CURRENT_TIMESTAMP, notes=excluded.notes""",
                         (import_name, import_name, package_name, 1 if installed else 0, version, notes))
            conn.commit()

    def dependency_recent(self) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            return [dict(r) for r in conn.execute('SELECT * FROM transport_dependencies ORDER BY package_name').fetchall()]

    def add_device(self, display_name: str, device_type: str, trust_state: str, notes: str = '', desired_transports: list[str] | None = None) -> str:
        self.initialize(); device_id = 'dev_' + uuid.uuid4().hex[:12]
        with self.connect() as conn:
            conn.execute("""INSERT INTO devices(device_id, display_name, device_type, trust_state, notes, desired_transports_json)
                   VALUES (?, ?, ?, ?, ?, ?)""", (device_id, display_name, device_type, trust_state, notes, json.dumps(desired_transports or [])))
            conn.commit()
        return device_id

    def delete_device(self, device_id: str) -> None:
        self.initialize()
        with self.connect() as conn:
            conn.execute('DELETE FROM devices WHERE device_id=?', (device_id,)); conn.commit()

    def list_devices(self) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute('SELECT * FROM devices ORDER BY updated_at DESC, created_at DESC').fetchall()
        out=[]
        for r in rows:
            item=dict(r)
            try: item['desired_transports']=json.loads(item.get('desired_transports_json') or '[]')
            except Exception: item['desired_transports']=[]
            out.append(item)
        return out

    def add_file_root(self, label: str, root_path: str, default_visibility: str, scan_enabled: bool, include_subfolders: bool, review_required: bool) -> str:
        self.initialize(); root_id='root_'+uuid.uuid4().hex[:12]
        with self.connect() as conn:
            conn.execute("""INSERT INTO file_roots(root_id, label, root_path, default_visibility, scan_enabled, include_subfolders, review_required)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""", (root_id, label, root_path, default_visibility, int(scan_enabled), int(include_subfolders), int(review_required)))
            conn.commit()
        return root_id

    def delete_file_root(self, root_id: str) -> None:
        self.initialize()
        with self.connect() as conn:
            conn.execute('DELETE FROM file_roots WHERE root_id=?', (root_id,)); conn.commit()

    def list_file_roots(self) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            rows = conn.execute('SELECT * FROM file_roots ORDER BY updated_at DESC, created_at DESC').fetchall()
        return [dict(r) for r in rows]

    def upsert_services(self, services: dict[str, dict[str, Any]]) -> None:
        self.initialize()
        with self.connect() as conn:
            for sid, data in services.items():
                conn.execute("""INSERT INTO services(service_id, enabled, visible_in_portal, requires_review, status)
                       VALUES (?, ?, ?, ?, ?) ON CONFLICT(service_id) DO UPDATE SET enabled=excluded.enabled,
                       visible_in_portal=excluded.visible_in_portal, requires_review=excluded.requires_review,
                       status=excluded.status, updated_at=CURRENT_TIMESTAMP""",
                    (sid, int(bool(data.get('enabled'))), int(bool(data.get('visible_in_portal'))), int(bool(data.get('requires_review'))), str(data.get('status','configured'))))
            conn.commit()


    def insert_catena_event(self, direction: str, line: str, parsed_type: str = '', result: str = '', error: str = '', port: str = '') -> str:
        event_id = 'cat_evt_' + uuid.uuid4().hex[:12]
        redacted = (line or '')[:500]
        with self.connect() as conn:
            conn.execute('INSERT INTO catena_events(event_id, port, direction, line_text_redacted, parsed_type, result, error) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (event_id, port, direction, redacted, parsed_type, result, error))
            conn.commit()
        return event_id

    def catena_events_recent(self, limit: int = 25) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            return [dict(r) for r in conn.execute('SELECT * FROM catena_events ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()]

    def insert_catena_message(self, message_id: str, payload_class: str, body_preview: str, serial_status: str, rf_status: str = 'not_proven', remote_ack_status: str = 'not_received', details: dict[str, Any] | None = None) -> None:
        with self.connect() as conn:
            conn.execute('INSERT OR REPLACE INTO catena_messages(message_id, payload_class, body_preview, serial_status, rf_status, remote_ack_status, details_json) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (message_id, payload_class, body_preview[:120], serial_status, rf_status, remote_ack_status, json.dumps(details or {}, sort_keys=True)))
            conn.commit()

    def catena_messages_recent(self, limit: int = 25) -> list[dict[str, Any]]:
        self.initialize()
        with self.connect() as conn:
            return [dict(r) for r in conn.execute('SELECT * FROM catena_messages ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()]


    def upsert_network_paths(self, paths: list[dict[str, Any]]) -> None:
        self.initialize()
        with self.connect() as conn:
            for p in paths:
                conn.execute("""INSERT INTO network_paths(path_id, adapter_name, ipv4_address, subnet_mask, gateway, dns_suffix, classification, recommendation_score, reason, suggested_url, source)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                              ON CONFLICT(path_id) DO UPDATE SET adapter_name=excluded.adapter_name, ipv4_address=excluded.ipv4_address,
                              subnet_mask=excluded.subnet_mask, gateway=excluded.gateway, dns_suffix=excluded.dns_suffix,
                              classification=excluded.classification, recommendation_score=excluded.recommendation_score, reason=excluded.reason,
                              suggested_url=excluded.suggested_url, source=excluded.source, last_seen_at=CURRENT_TIMESTAMP""",
                             (p.get('path_id'), p.get('adapter_name',''), p.get('ipv4_address',''), p.get('subnet_mask',''), p.get('gateway',''), p.get('dns_suffix',''), p.get('classification',''), int(p.get('recommendation_score',0)), p.get('reason',''), p.get('suggested_url',''), p.get('source','')))
            conn.commit()

    def select_network_path(self, path: dict[str, Any]) -> None:
        self.initialize()
        with self.connect() as conn:
            conn.execute('INSERT OR REPLACE INTO selected_network_path(selected_id, path_id, url_base) VALUES (?, ?, ?)', ('active', path.get('path_id',''), (path.get('suggested_url') or '').rstrip('/')))
            conn.commit()

    def selected_network_path_row(self) -> dict[str, Any] | None:
        self.initialize()
        with self.connect() as conn:
            row = conn.execute('SELECT * FROM selected_network_path WHERE selected_id=?', ('active',)).fetchone()
        return dict(row) if row else None

    def table_counts(self) -> dict[str, int]:
        self.initialize()
        tables = ['schema_meta','config_kv','config_snapshots','config_changes','audit_events','devices','file_roots','services','policy_rules','roles','users_local',
                  'auth_credentials','sessions','permission_grants','permission_requests','password_reset_requests','mail_messages','mail_recipients','bbs_posts',
                  'transport_adapters','messages','delivery_attempts','runtime_events','support_exports','peers','peer_handshakes','transport_dependencies',
                  'route_decisions','adapter_events','network_events','node_identity','peer_invites','hardware_devices','serial_devices','catena_events','catena_messages','nav_events','network_paths','selected_network_path']
        counts: dict[str, int] = {}
        with self.connect() as conn:
            for table in tables:
                try: counts[table] = int(conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0])
                except sqlite3.Error: counts[table] = -1
        return counts
