
import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, -- 'Notice', 'Late Arrival', 'Holiday'
        title TEXT,
    content TEXT,
    date TEXT
);