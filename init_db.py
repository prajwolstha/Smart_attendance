import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "attendance.db")

def fix_duplicates():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # This removes all rows from the announcements and syllabus tables
    cursor.execute("DELETE FROM announcements")
    cursor.execute("DELETE FROM syllabus")
    
    # Optional: Reset the ID counter
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='announcements'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='syllabus'")
    
    conn.commit()
    conn.close()
    print("✅ Duplicates cleared. Now run your init script ONCE to repopulate.")

if __name__ == "__main__":
    fix_duplicates()