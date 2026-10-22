import sqlite3

# Connect to (or create) the database file
connection = sqlite3.connect('database.db')

# Create a cursor - this lets us run SQL commands
cursor = connection.cursor()

# Create the STUDENTS table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    department TEXT NOT NULL,
    year TEXT NOT NULL
)
''')

# Create the HOD table
cursor.execute('''
CREATE TABLE IF NOT EXISTS hod (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Create the PROBLEMS table
cursor.execute('''
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    attachment TEXT,
    status TEXT NOT NULL DEFAULT 'Pending',
    hod_reply TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id)
)
''')

# Save the changes
connection.commit()

# Close the connection
connection.close()

print("Database and tables created successfully!")