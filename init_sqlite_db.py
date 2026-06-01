
import csv
import sqlite3
import os

def init_database():
    # Database file path
    db_path = os.path.join(os.path.dirname(__file__), "data", "students.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database (will create if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create students table - use TEXT for factor_1/factor_2 since they are lists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            academic_year TEXT,
            grade_level TEXT,
            class TEXT,
            parent TEXT,
            parent_phone TEXT,
            email TEXT,
            Math_factor_1 TEXT,
            Math_factor_2 TEXT,
            Math_factor_3 REAL,
            Math_gpa REAL,
            Literature_factor_1 TEXT,
            Literature_factor_2 TEXT,
            Literature_factor_3 REAL,
            Literature_gpa REAL,
            English_factor_1 TEXT,
            English_factor_2 TEXT,
            English_factor_3 REAL,
            English_gpa REAL,
            Physics_factor_1 TEXT,
            Physics_factor_2 TEXT,
            Physics_factor_3 REAL,
            Physics_gpa REAL,
            Chemistry_factor_1 TEXT,
            Chemistry_factor_2 TEXT,
            Chemistry_factor_3 REAL,
            Chemistry_gpa REAL,
            Biology_factor_1 TEXT,
            Biology_factor_2 TEXT,
            Biology_factor_3 REAL,
            Biology_gpa REAL,
            History_factor_1 TEXT,
            History_factor_2 TEXT,
            History_factor_3 REAL,
            History_gpa REAL,
            Geography_factor_1 TEXT,
            Geography_factor_2 TEXT,
            Geography_factor_3 REAL,
            Geography_gpa REAL,
            excused_absences INTEGER,
            unexcused_absences INTEGER,
            behavior_score REAL,
            conduct_grade TEXT,
            overall_gpa REAL,
            teacher_remarks TEXT,
            UNIQUE(student_id, academic_year)
        )
    ''')
    
    # Import data from CSV
    csv_path = os.path.join(os.path.dirname(__file__), "database_master.csv")
    with open(csv_path, 'r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        print("Headers:", csv_reader.fieldnames)
        for row in csv_reader:
            # Convert numeric fields from strings
            # Factor 1 and 2 are lists, keep as string, but convert semicolons to commas for consistency
            for subj in ['Math', 'Literature', 'English', 'Physics', 'Chemistry', 'Biology', 'History', 'Geography']:
                # Process factor_1 and factor_2: keep as string, but normalize separators
                for factor in ['_factor_1', '_factor_2']:
                    key = subj + factor
                    if row[key]:
                        # Replace ';' with ',' for list separator, and '.' for decimal
                        row[key] = row[key].replace(';', ',')
                    else:
                        row[key] = None
                # Process factor_3 and gpa
                key = subj + '_factor_3'
                if row[key]:
                    row[key] = float(row[key].replace(';', '.'))
                else:
                    row[key] = None
                key = subj + '_gpa'
                if row[key]:
                    row[key] = float(row[key].replace(';', '.'))
                else:
                    row[key] = None
            # Process other numeric fields
            for field in ['excused_absences', 'unexcused_absences']:
                if row[field]:
                    row[field] = int(row[field])
                else:
                    row[field] = None
            for field in ['behavior_score', 'overall_gpa']:
                if row[field]:
                    row[field] = float(row[field].replace(';', '.'))
                else:
                    row[field] = None
            
            cursor.execute('''
                INSERT OR REPLACE INTO students (
                    student_id, name, academic_year, grade_level, class, parent, parent_phone, email,
                    Math_factor_1, Math_factor_2, Math_factor_3, Math_gpa,
                    Literature_factor_1, Literature_factor_2, Literature_factor_3, Literature_gpa,
                    English_factor_1, English_factor_2, English_factor_3, English_gpa,
                    Physics_factor_1, Physics_factor_2, Physics_factor_3, Physics_gpa,
                    Chemistry_factor_1, Chemistry_factor_2, Chemistry_factor_3, Chemistry_gpa,
                    Biology_factor_1, Biology_factor_2, Biology_factor_3, Biology_gpa,
                    History_factor_1, History_factor_2, History_factor_3, History_gpa,
                    Geography_factor_1, Geography_factor_2, Geography_factor_3, Geography_gpa,
                    excused_absences, unexcused_absences, behavior_score, conduct_grade, overall_gpa, teacher_remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['student_id'], row['name'], row['academic_year'], row['grade_level'], row['class'], row['parent'], 
                row['parent_phone'], row['email'], row['Math_factor_1'], row['Math_factor_2'], row['Math_factor_3'], 
                row['Math_gpa'], row['Literature_factor_1'], row['Literature_factor_2'], row['Literature_factor_3'], 
                row['Literature_gpa'], row['English_factor_1'], row['English_factor_2'], row['English_factor_3'], 
                row['English_gpa'], row['Physics_factor_1'], row['Physics_factor_2'], row['Physics_factor_3'], 
                row['Physics_gpa'], row['Chemistry_factor_1'], row['Chemistry_factor_2'], row['Chemistry_factor_3'], 
                row['Chemistry_gpa'], row['Biology_factor_1'], row['Biology_factor_2'], row['Biology_factor_3'], 
                row['Biology_gpa'], row['History_factor_1'], row['History_factor_2'], row['History_factor_3'], 
                row['History_gpa'], row['Geography_factor_1'], row['Geography_factor_2'], row['Geography_factor_3'], 
                row['Geography_gpa'], row['excused_absences'], row['unexcused_absences'], row['behavior_score'], 
                row['conduct_grade'], row['overall_gpa'], row['teacher_remarks']
            ))
    
    # Commit changes
    conn.commit()
    print("Database initialized successfully!")
    print(f"Imported {cursor.rowcount} students")
    conn.close()

if __name__ == "__main__":
    init_database()
