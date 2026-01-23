import sqlite3
import json
from typing import List, Dict
from pathlib import Path

DB_PATH = Path("data/chat_history.db")

class ChatStore:
    def __init__(self):
        # Ensure data directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                date TEXT
            )
        ''')
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                sources TEXT, -- JSON string
                generation_time REAL,
                FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def create_session(self, session_id: str, title: str, date: str):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO sessions (id, title, date) VALUES (?, ?, ?)', 
                       (session_id, title, date))
        self.conn.commit()

    def get_sessions(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title, date FROM sessions ORDER BY date DESC, id DESC')
        rows = cursor.fetchall()
        return [{"id": r[0], "title": r[1], "date": r[2], "messages": []} for r in rows]

    def update_session_title(self, session_id: str, title: str):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE sessions SET title = ? WHERE id = ?', (title, session_id))
        self.conn.commit()

    def delete_session(self, session_id: str):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
        self.conn.commit()

    def add_message(self, session_id: str, role: str, content: str, sources: List = None, generation_time: float = 0.0):
        cursor = self.conn.cursor()
        sources_json = json.dumps(sources) if sources else "[]"
        cursor.execute('''
            INSERT INTO messages (session_id, role, content, sources, generation_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, role, content, sources_json, generation_time))
        self.conn.commit()

    def get_messages(self, session_id: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT role, content, sources, generation_time 
            FROM messages WHERE session_id = ? ORDER BY id ASC
        ''', (session_id,))
        rows = cursor.fetchall()
        return [{
            "role": r[0],
            "content": r[1],
            "sources": json.loads(r[2]),
            "generation_time": r[3]
        } for r in rows]

    def close(self):
        self.conn.close()