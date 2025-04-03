# user_db.py
import sqlite3
from passlib.context import CryptContext
from typing import Optional, Dict
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserDB:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT,
                    email TEXT,
                    disabled BOOLEAN DEFAULT FALSE,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            conn.commit()

            # Create admin user if not exists
            if not self.get_user("admin"):
                self.create_user(
                    username="admin",
                    password="admin123",  # Change this in production!
                    full_name="Admin User",
                    email="admin@example.com",
                    role="admin"
                )

    def create_user(self, username: str, password: str, **kwargs):
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO users (
                        username, 
                        hashed_password,
                        full_name,
                        email,
                        role
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    username,
                    pwd_context.hash(password),
                    kwargs.get("full_name", ""),
                    kwargs.get("email", ""),
                    kwargs.get("role", "user")
                ))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def get_user(self, username: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if user := cursor.fetchone():
                return dict(user)
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        if user := self.get_user(username):
            if pwd_context.verify(password, user["hashed_password"]):
                # Update last login time
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "UPDATE users SET last_login = ? WHERE username = ?",
                        (datetime.now(), username)
                    )
                    conn.commit()
                return user
        return None

    def update_last_login(self, username: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET last_login = ? WHERE username = ?",
                (datetime.now(), username)
            )
            conn.commit()