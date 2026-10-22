from app import app, db, Student, HOD, Problem, Comment
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        # Drop and create tables
        db.drop_all()
        db.create_all()

        # Create HOD
        hod_username = 'hod_admin'
        hod_password = 'hod123'
        hashed_hod_password = generate_password_hash(hod_password)
        hod = HOD(username=hod_username, password=hashed_hod_password)
        db.session.add(hod)

        # Create Student
        student_name = 'Chaitanya Deshmukh'
        student_email = 'chaitanya@example.com'
        student_password = 'student123'
        hashed_student_password = generate_password_hash(student_password)
        student = Student(
            name=student_name,
            email=student_email,
            password=hashed_student_password,
            department='Computer Engineering',
            year='3rd Year'
        )
        db.session.add(student)
        
        # Commit to get the IDs
        db.session.commit()

        print("Test HOD and Student accounts created successfully!")
        print(f"HOD login -> username: {hod_username} | password: {hod_password}")
        print(f"Student login -> email: {student_email} | password: {student_password}")

if __name__ == '__main__':
    seed_data()