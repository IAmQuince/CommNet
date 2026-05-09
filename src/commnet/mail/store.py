from __future__ import annotations

import uuid
from typing import Any


class MailStore:
    def __init__(self, store, audit=None):
        self.store = store
        self.audit = audit
        self.store.initialize()

    def send(self, sender_user_id: str, recipient_user_ids: list[str], subject: str, body: str, system_message: bool = False, broadcast: bool = False) -> str:
        subject = (subject or '').strip()[:160] or '(no subject)'
        body = (body or '').strip()[:5000]
        if not recipient_user_ids:
            raise ValueError('At least one recipient is required.')
        message_id = 'mail_' + uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute('INSERT INTO mail_messages(message_id, sender_user_id, subject, body, system_message, broadcast) VALUES (?, ?, ?, ?, ?, ?)',
                         (message_id, sender_user_id, subject, body, int(system_message), int(broadcast)))
            for uid in recipient_user_ids:
                conn.execute('INSERT INTO mail_recipients(message_id, recipient_user_id) VALUES (?, ?)', (message_id, uid))
            conn.commit()
        if self.audit:
            self.audit.write('mail_sent', {'message_id': message_id, 'sender_user_id': sender_user_id, 'recipient_count': len(recipient_user_ids), 'broadcast': broadcast})
        return message_id

    def inbox(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute('''SELECT m.*, r.read_at, r.deleted_at, u.display_name AS sender_name
                                   FROM mail_recipients r JOIN mail_messages m ON m.message_id=r.message_id
                                   LEFT JOIN users_local u ON u.user_id=m.sender_user_id
                                   WHERE r.recipient_user_id=? AND r.deleted_at IS NULL
                                   ORDER BY m.created_at DESC LIMIT ?''', (user_id, limit)).fetchall()
        return [dict(r) for r in rows]

    def sent(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute('SELECT * FROM mail_messages WHERE sender_user_id=? ORDER BY created_at DESC LIMIT ?', (user_id, limit)).fetchall()
        return [dict(r) for r in rows]

    def unread_count(self, user_id: str) -> int:
        with self.store.connect() as conn:
            row = conn.execute('SELECT COUNT(*) FROM mail_recipients WHERE recipient_user_id=? AND read_at IS NULL AND deleted_at IS NULL', (user_id,)).fetchone()
        return int(row[0])

    def read(self, message_id: str, user_id: str | None = None) -> dict[str, Any] | None:
        with self.store.connect() as conn:
            if user_id:
                conn.execute('UPDATE mail_recipients SET read_at=CURRENT_TIMESTAMP WHERE message_id=? AND recipient_user_id=? AND read_at IS NULL', (message_id, user_id))
            row = conn.execute('''SELECT m.*, u.display_name AS sender_name FROM mail_messages m
                                  LEFT JOIN users_local u ON u.user_id=m.sender_user_id WHERE m.message_id=?''', (message_id,)).fetchone()
            recipients = conn.execute('''SELECT r.*, u.display_name, c.username FROM mail_recipients r
                                         LEFT JOIN users_local u ON u.user_id=r.recipient_user_id
                                         LEFT JOIN auth_credentials c ON c.user_id=r.recipient_user_id
                                         WHERE r.message_id=?''', (message_id,)).fetchall()
            conn.commit()
        if not row:
            return None
        data = dict(row)
        data['recipients'] = [dict(r) for r in recipients]
        return data
