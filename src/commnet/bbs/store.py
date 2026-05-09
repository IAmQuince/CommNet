from __future__ import annotations
import uuid
from typing import Any
DEFAULT_BOARDS=[('announcements','Announcements','Pinned local announcements and node updates.'),('general','General','General local discussion.'),('help','Help','Ask for help joining, finding files, or using CommNet.'),('retroweb','RetroWeb','RetroWeb recommendations, comments, and review notes.'),('emergency','Emergency / Outage','Local priority messages during outages or emergency mode.')]
WELCOME_BODY='''Welcome to the CommNet BBS.\n\nThis is a local message board hosted by this CommNet node. Use it for local announcements, help requests, project notes, RetroWeb discussions, and offline community messages.\n\nBoards, threads, replies, pinned posts, and locked threads are intentionally small and local-first in this run.'''
class BBSStore:
    def __init__(self, store, audit=None): self.store=store; self.audit=audit; self.store.initialize()
    def ensure_seed(self)->None:
        with self.store.connect() as conn:
            for i,(board_id,title,desc) in enumerate(DEFAULT_BOARDS): conn.execute('INSERT OR IGNORE INTO bbs_boards(board_id,title,description,sort_order) VALUES (?,?,?,?)',(board_id,title,desc,i*10))
            row=conn.execute("SELECT COUNT(*) FROM bbs_threads WHERE seed_key='welcome' AND status!='deleted'").fetchone()
            if int(row[0])==0:
                tid='thread_'+uuid.uuid4().hex[:12]; rid='reply_'+uuid.uuid4().hex[:12]
                conn.execute("INSERT INTO bbs_threads(thread_id,board_id,title,author_user_id,pinned,locked,seed_key) VALUES (?,'announcements','Welcome to the CommNet BBS','',1,0,'welcome')",(tid,))
                conn.execute('INSERT INTO bbs_replies(reply_id,thread_id,author_user_id,body) VALUES (?,?,?,?)',(rid,tid,'',WELCOME_BODY))
            conn.commit()
    def boards(self)->list[dict[str,Any]]:
        self.ensure_seed();
        with self.store.connect() as conn: rows=conn.execute("""SELECT b.*, COUNT(t.thread_id) AS thread_count, MAX(t.updated_at) AS last_activity FROM bbs_boards b LEFT JOIN bbs_threads t ON t.board_id=b.board_id AND t.status!='deleted' GROUP BY b.board_id ORDER BY b.sort_order,b.title""").fetchall()
        return [dict(r) for r in rows]
    def board(self, board_id:str)->dict[str,Any]|None:
        self.ensure_seed();
        with self.store.connect() as conn: row=conn.execute('SELECT * FROM bbs_boards WHERE board_id=?',(board_id,)).fetchone()
        return dict(row) if row else None
    def threads(self, board_id:str|None=None, limit:int=50, offset:int=0)->list[dict[str,Any]]:
        self.ensure_seed();
        with self.store.connect() as conn:
            if board_id: rows=conn.execute("""SELECT t.*, b.title AS board_title, u.display_name AS author_name, COUNT(r.reply_id) AS reply_count, MAX(r.created_at) AS last_reply_at FROM bbs_threads t JOIN bbs_boards b ON b.board_id=t.board_id LEFT JOIN bbs_replies r ON r.thread_id=t.thread_id AND r.status!='deleted' LEFT JOIN users_local u ON u.user_id=t.author_user_id WHERE t.board_id=? AND t.status!='deleted' GROUP BY t.thread_id ORDER BY t.pinned DESC, COALESCE(last_reply_at,t.created_at) DESC LIMIT ? OFFSET ?""",(board_id,limit,offset)).fetchall()
            else: rows=conn.execute("""SELECT t.*, b.title AS board_title, u.display_name AS author_name, COUNT(r.reply_id) AS reply_count, MAX(r.created_at) AS last_reply_at FROM bbs_threads t JOIN bbs_boards b ON b.board_id=t.board_id LEFT JOIN bbs_replies r ON r.thread_id=t.thread_id AND r.status!='deleted' LEFT JOIN users_local u ON u.user_id=t.author_user_id WHERE t.status!='deleted' GROUP BY t.thread_id ORDER BY t.pinned DESC, COALESCE(last_reply_at,t.created_at) DESC LIMIT ? OFFSET ?""",(limit,offset)).fetchall()
        return [dict(r) for r in rows]
    def thread(self, thread_id:str)->dict[str,Any]|None:
        self.ensure_seed();
        with self.store.connect() as conn: row=conn.execute("""SELECT t.*, b.title AS board_title, u.display_name AS author_name FROM bbs_threads t JOIN bbs_boards b ON b.board_id=t.board_id LEFT JOIN users_local u ON u.user_id=t.author_user_id WHERE t.thread_id=? AND t.status!='deleted'""",(thread_id,)).fetchone()
        return dict(row) if row else None
    def replies(self, thread_id:str, limit:int=100)->list[dict[str,Any]]:
        with self.store.connect() as conn: rows=conn.execute("""SELECT r.*, u.display_name AS author_name FROM bbs_replies r LEFT JOIN users_local u ON u.user_id=r.author_user_id WHERE r.thread_id=? AND r.status!='deleted' ORDER BY r.created_at ASC LIMIT ?""",(thread_id,limit)).fetchall()
        return [dict(r) for r in rows]
    def create_thread(self, board_id:str, title:str, body:str, author_user_id:str='')->str:
        title=(title or 'Untitled thread').strip()[:160]; body=(body or '').strip()[:5000] or '(no body)'; tid='thread_'+uuid.uuid4().hex[:12]; rid='reply_'+uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            conn.execute('INSERT INTO bbs_threads(thread_id,board_id,title,author_user_id) VALUES (?,?,?,?)',(tid,board_id[:40],title,author_user_id[:80])); conn.execute('INSERT INTO bbs_replies(reply_id,thread_id,author_user_id,body) VALUES (?,?,?,?)',(rid,tid,author_user_id[:80],body)); conn.commit()
        if self.audit: self.audit.write('bbs_thread_created', {'thread_id':tid,'board_id':board_id,'author_user_id':author_user_id})
        return tid
    def reply(self, thread_id:str, body:str, author_user_id:str='')->str:
        body=(body or '').strip()[:5000]
        if not body: raise ValueError('Reply body is required.')
        rid='reply_'+uuid.uuid4().hex[:12]
        with self.store.connect() as conn:
            t=conn.execute('SELECT locked FROM bbs_threads WHERE thread_id=?',(thread_id,)).fetchone()
            if not t: raise ValueError('Thread not found.')
            if int(t['locked'] or 0): raise ValueError('Thread is locked.')
            conn.execute('INSERT INTO bbs_replies(reply_id,thread_id,author_user_id,body) VALUES (?,?,?,?)',(rid,thread_id,author_user_id[:80],body)); conn.execute('UPDATE bbs_threads SET updated_at=CURRENT_TIMESTAMP WHERE thread_id=?',(thread_id,)); conn.commit()
        if self.audit: self.audit.write('bbs_reply_created', {'thread_id':thread_id,'reply_id':rid,'author_user_id':author_user_id})
        return rid
