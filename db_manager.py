import sqlite3

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the conversations table if it doesn't exist."""
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()

def add_message(session_id, role, content):
    """Adds a new message to the conversations table."""
    conn = get_db_connection()
    conn.execute('INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)',
                 (session_id, role, content))
    conn.commit()
    conn.close()

def get_conversation(session_id):
    """Retrieves the conversation history for a given session ID."""
    conn = get_db_connection()
    messages = conn.execute('SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp ASC',
                            (session_id,)).fetchall()
    conn.close()
    return messages