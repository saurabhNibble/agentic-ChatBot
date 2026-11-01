
import sqlite3
import uuid
from datetime import datetime


class ThreadDatabase:

    def __init__(self, db_name="chat_memory.db"):
        self.db_name = db_name
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    # 1. CREATE TABLE
    def create_table(self):

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    thread_id TEXT PRIMARY KEY,
                    thread_name TEXT,
                    created_at TEXT
                )
            """)

    # 2. CREATE NEW THREAD
    def create_thread(self, thread_name="New Chat"):

        thread_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO threads
                (thread_id, thread_name, created_at)
                VALUES (?, ?, ?)
            """, (thread_id, thread_name, created_at))

        return thread_id

    # 3. GET ALL THREADS
    def get_all_threads(self):

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT thread_id, thread_name, created_at
                FROM threads
                ORDER BY created_at DESC
            """)

            return cursor.fetchall()

    # 4. UPDATE THREAD TITLE
    def update_thread_title(self, thread_id, thread_name):

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE threads
                SET thread_name = ?
                WHERE thread_id = ?
            """, (thread_name, thread_id))

            return cursor.rowcount > 0

    # 5. DELETE THREAD METADATA
    def delete_thread(self, thread_id):

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM threads
                WHERE thread_id = ?
            """, (thread_id,))

            return cursor.rowcount > 0


# Initialize database
db = ThreadDatabase()
