from app import app, db, Authenticate, Student, bcrypt, AttendanceRecord, TimeTable, markedAttendance
import pandas as pd
# Create an application context
with app.app_context():
    try:
        # Create the database and the db table
        db.create_all()

        # Use session.no_autoflush context manager to disable autoflush temporarily
        with db.session.no_autoflush:
            # Insert user data
            hashed_password1 = bcrypt.generate_password_hash('devtest123').decode('utf-8')
            user1 = Authenticate(username='devtest', password=hashed_password1)

            hashed_password2 = bcrypt.generate_password_hash('test').decode('utf-8')
            user2 = Authenticate(username='test', password=hashed_password2)

            db.session.add(user1)
            db.session.add(user2)   
            # commit the changes without autoflush
            db.session.commit()

            # Insert student data
            
            df = pd.read_excel('student_data.xlsx')

    # Iterate through rows and add data to the 'students' table
            for index, row in df.iterrows():
                student = Student(
                    roll_no=row['roll_no'],
                    name=row['name'],
                    enrollment_no=row['enrollment_no']
                )
                db.session.add(student)

            df = pd.read_excel('TimeTable.xlsx')

    # Iterate through rows and add data to the 'students' table
            for index, row in df.iterrows():
                tb= TimeTable(
                    batch = row['batch'],
                    day = row['day'],
                    slot1 = row['slot1'],
                    slot2 = row['slot2'],
                    slot3 = row['slot3'],
                    slot4 = row['slot4'],
                    slot5 = row['slot5'],
                    slot6 = row['slot6'],
                    slot7 = row['slot7'],
                    slot8 = row['slot8'],
                )
                db.session.add(tb)

            db.session.commit()

    except Exception as e:
        print(f"Error during database creation: {e}")