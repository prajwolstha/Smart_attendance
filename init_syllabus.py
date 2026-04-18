import sqlite3
import os

# Path to your database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")

def setup_full_curriculum():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # CRITICAL: Drop the old table to fix the "no column named program" error
    cursor.execute("DROP TABLE IF EXISTS syllabus")

    # Recreate the table with the 'program' column
    cursor.execute('''CREATE TABLE syllabus 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       program TEXT, 
                       semester TEXT, 
                       subject TEXT, 
                       link TEXT)''')

    # Data for BCA (8 Semesters)
    bca_data = [
        ('BCA', '1st', 'Computer Fundamentals & Applications', ''),
        ('BCA', '1st', 'Society and Technology', ''),
        ('BCA', '1st', 'English I', ''),
        ('BCA', '1st', 'Mathematics I', ''),
        ('BCA', '1st', 'Digital Logic', ''),
        ('BCA', '2nd', 'C Programming', ''),
        ('BCA', '2nd', 'Financial Accounting', ''),
        ('BCA', '2nd', 'English II', ''),
        ('BCA', '2nd', 'Mathematics II', ''),
        ('BCA', '2nd', 'Microprocessor & Computer Architecture', ''),
        ('BCA', '3rd', 'Data Structures and Algorithms', ''),
        ('BCA', '3rd', 'Probability & Statistics', ''),
        ('BCA', '3rd', 'System Analysis and Design', ''),
        ('BCA', '3rd', 'Java Programming I', ''),
        ('BCA', '3rd', 'Web Technology I', ''),
        ('BCA', '4th', 'Operating System', ''),
        ('BCA', '4th', 'Numerical Methods', ''),
        ('BCA', '4th', 'Software Engineering', ''),
        ('BCA', '4th', 'Scripting Language', ''),
        ('BCA', '4th', 'Database Management System', ''),
        ('BCA', '5th', 'MIS and E-Business', ''),
        ('BCA', '5th', 'DotNet Technology', ''),
        ('BCA', '5th', 'Computer Networking', ''),
        ('BCA', '5th', 'Introduction to Management', ''),
        ('BCA', '5th', 'Computer Graphics and Animation', ''),
        ('BCA', '6th', 'Mobile Programming', ''),
        ('BCA', '6th', 'Distributed System', ''),
        ('BCA', '6th', 'Applied Economics', ''),
        ('BCA', '6th', 'Advanced Java Programming', ''),
        ('BCA', '6th', 'Network Security', ''),
        ('BCA', '7th', 'Cyber Law & Professional Ethics', ''),
        ('BCA', '7th', 'Cloud Computing', ''),
        ('BCA', '7th', 'Internship', ''),
        ('BCA', '7th', 'Elective I', ''),
        ('BCA', '8th', 'Operations Research', ''),
        ('BCA', '8th', 'Project (Part II)', ''),
        ('BCA', '8th', 'Elective III', ''),
        ('BCA', '8th', 'Elective IV', '')
    ]

    # Data for CSIT (8 Semesters)
    csit_data = [
        ('CSIT', '1st', 'Introduction to IT', ''),
        ('CSIT', '1st', 'C Programming', ''),
        ('CSIT', '1st', 'Digital Logic', ''),
        ('CSIT', '1st', 'Mathematics I', ''),
        ('CSIT', '1st', 'Physics', ''),
        ('CSIT', '2nd', 'Discrete Structure', ''),
        ('CSIT', '2nd', 'Object Oriented Programming', ''),
        ('CSIT', '2nd', 'Microprocessor', ''),
        ('CSIT', '2nd', 'Mathematics II', ''),
        ('CSIT', '2nd', 'Statistics I', ''),
        ('CSIT', '3rd', 'Data Structures and Algorithms', ''),
        ('CSIT', '3rd', 'Numerical Methods', ''),
        ('CSIT', '3rd', 'Computer Architecture', ''),
        ('CSIT', '3rd', 'Computer Graphics', ''),
        ('CSIT', '3rd', 'Statistics II', ''),
        ('CSIT', '4th', 'Theory of Computation', ''),
        ('CSIT', '4th', 'Computer Networks', ''),
        ('CSIT', '4th', 'Operating Systems', ''),
        ('CSIT', '4th', 'DBMS', ''),
        ('CSIT', '4th', 'Artificial Intelligence', ''),
        ('CSIT', '5th', 'Design and Analysis of Algorithms', ''),
        ('CSIT', '5th', 'System Analysis and Design', ''),
        ('CSIT', '5th', 'Cryptography', ''),
        ('CSIT', '5th', 'Simulation and Modeling', ''),
        ('CSIT', '5th', 'Web Technology', ''),
        ('CSIT', '6th', 'Software Engineering', ''),
        ('CSIT', '6th', 'Compiler Design and Construction', ''),
        ('CSIT', '6th', 'Web-Centric Computing', ''),
        ('CSIT', '6th', 'Real-Time Systems', ''),
        ('CSIT', '7th', 'Advanced Java Programming', ''),
        ('CSIT', '7th', 'Data Warehousing and Data Mining', ''),
        ('CSIT', '7th', 'Principles of Management', ''),
        ('CSIT', '7th', 'Project work', ''),
        ('CSIT', '8th', 'Advanced Database', ''),
        ('CSIT', '8th', 'Internship', ''),
        ('CSIT', '8th', 'Network and System Administration', '')
    ]

    # Insert data
    cursor.executemany("INSERT INTO syllabus (program, semester, subject, link) VALUES (?, ?, ?, ?)", bca_data)
    cursor.executemany("INSERT INTO syllabus (program, semester, subject, link) VALUES (?, ?, ?, ?)", csit_data)

    conn.commit()
    conn.close()
    print("✅ Syllabus database rebuilt with BCA and CSIT subjects.")

if __name__ == "__main__":
    setup_full_curriculum()