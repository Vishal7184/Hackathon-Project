from flask_socketio import SocketIO
from flask import Flask, render_template, redirect, url_for, session, request, flash, get_flashed_messages
from flask import Response,jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from flask_bcrypt import Bcrypt
import cv2, sys, numpy as np, json, os, base64, joblib
from io import BytesIO
from PIL import Image,UnidentifiedImageError
import os, io, base64, logging
from time import sleep
import pandas as pd
from werkzeug.utils import secure_filename 
import subprocess

import pandas as pd
app = Flask(__name__)
@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

socketio = SocketIO(app)

# Use SQLite database file named 'users.db' located in the project directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

class Authenticate(db.Model, UserMixin):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.username} - {self.password}"
    def get_id(self):
        return str(self.sno)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    enrollment_no = db.Column(db.String(20), unique=True, nullable=False)
    def __repr__(self):
        return f"{self.roll_number} - {self.name}"

# class AttendanceRecord(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     roll_no = db.Column(db.String(20), unique=True, nullable=False)
#     name = db.Column(db.String(200), nullable=False)
#     enrollment_no = db.Column(db.String(20), unique=True, nullable=False)
#     subject_name = db.Column(db.String(200),nullable=False)
#     batch = db.Column(db.String(20))
#     slot_type = db.Column(db.String(200),nullable=False)
#     date = db.Column(db.Date,nullable=False)
#     present = db.Column(db.String(1),default='n') # n means absent

#     def __repr__(self):
#         return f"{self.roll_number} - {self.name}"

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,nullable=False)
    batch = db.Column(db.String(20),nullable=False)
    slot = db.Column(db.String(200),nullable=False)
    roll_no = db.Column(db.String(20),nullable=False)
    name = db.Column(db.String(200),nullable=False)
    enrollment_no = db.Column(db.String(20),nullable=False)
    present = db.Column(db.String(1),default='n') # n means absent

class TimeTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch = db.Column(db.String(20), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    slot1 = db.Column(db.String(200))
    slot2 = db.Column(db.String(200))
    slot3 = db.Column(db.String(200))
    slot4 = db.Column(db.String(200))
    slot5 = db.Column(db.String(200))
    slot6 = db.Column(db.String(200))
    slot7 = db.Column(db.String(200))
    slot8 = db.Column(db.String(200))
    def __repr__(self):
        return f"{self.day}"

class markedAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date,nullable=False)
    batch = db.Column(db.String(20),nullable=False)
    slot = db.Column(db.String(200),nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Authenticate.query.get(int(user_id))

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        pwd = request.form['pwd']

        user = Authenticate.query.filter_by(username=uname).first()
        if user and bcrypt.check_password_hash(user.password, pwd):
            login_user(user)
            if current_user.is_authenticated:
                flash('Login Successful!','info')
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template("login.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html") 

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

@app.route('/addstudent')
def to_addStudent():
    return render_template('addStudent.html')

@app.route('/uploadStudentData')
def to_uploadStudentData():
    return render_template('uploadStudentData.html')

@app.route('/markattendance')
def to_markAttendance():
    return render_template('markAttendance.html')

@socketio.on('load_lectures')
def handle_load_lectures(data):
    print("Here")
    selected_day = data['selectedDay']
    print(selected_day)
    selected_batch = data['selectedBatch']
    print(selected_batch)
    if(selected_batch=="Lecture"):
        slots_data = TimeTable.query.filter_by(batch='1', day=selected_day).first()
        # Check if slots_data is not None to avoid errors
        if slots_data:
            print("Here i Am")
            # Iterate through each attribute of the record
            for attr, value in vars(slots_data).items():
                value_str = str(value)
                if '[PR]' in value_str:
                    # If it contains '[PR]', replace the value with an empty string
                    setattr(slots_data, attr, value_str.replace(value_str, '-'))
    else:    
        # Use SQLAlchemy to query the database
        slots_data = TimeTable.query.filter_by(batch=selected_batch, day=selected_day).first()
        if slots_data:
            print("Here i Am")
            # Iterate through each attribute of the record
            for attr_name in slots_data.__table__.columns.keys():
                # Get the value of the attribute
                value = getattr(slots_data, attr_name)
                # Convert the value to a string
                value_str = str(value)
                if '[PR]' not in value_str:
                    # If it doesn't contain '[PR]', replace the value with '-'
                    setattr(slots_data, attr_name, '-')
    # Convert the result to a dictionary for sending over Socket.IO
    slots_data_dict = {
        'slot1': slots_data.slot1,
        'slot2': slots_data.slot2,
        'slot3': slots_data.slot3,
        'slot4': slots_data.slot4,
        'slot5': slots_data.slot5
    }
    # Emit the response back to the client
    slots_data_list = list(slots_data_dict.values())
    for item in slots_data_list:
        print(item)
    socketio.emit('lectures_loaded', slots_data_list)

@app.route("/showAttendance", methods = ['POST'])
@login_required
def showAttendance():
    try:   
        selected_day_str = request.form['selectedDay']
        selected_day = datetime.strptime(selected_day_str, "%a %b %d %Y %H:%M:%S GMT%z (%Z)")  
        dte = selected_day.strftime("%A, %d %B %Y")
        selected_batch = request.form['selectedBatch']
        if(selected_batch == "Lecture"):
            selected_batch='L'
        selected_slot = request.form['selectedSlot']
        print(selected_day.date(),selected_batch,selected_slot)
        attendanceRecord = AttendanceRecord.query.filter_by(date=selected_day.date(), batch=selected_batch, slot=selected_slot).order_by(AttendanceRecord.roll_no).all()
        attendance_data = []
        for record in attendanceRecord:
            attendance_data.append({
                'roll_no': record.roll_no,
                'name': record.name,
                'enrollment_no': record.enrollment_no,
                'present': record.present
                # Add more fields as needed
            })
        count = len(attendance_data)
        print(attendance_data)
        if(selected_batch == "L"):
            selected_batch="Lecture"
        elif(selected_batch=="1"):
            selected_batch="IF1"
        elif(selected_batch=="2"):
            selected_batch="IF2"
        elif(selected_batch=="3"):
            selected_batch="IF3"
        # result = AttendanceRecord.query.with_entities(AttendanceRecord.date, AttendanceRecord.subject, AttendanceRecord.batch).first()
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching attendance data'})
        return []
    print(attendance_data,count,dte, selected_batch, selected_slot)
    return jsonify({'attendance': attendance_data,'count': count, 'selected_day':dte,'selected_batch':selected_batch,'selected_slot':selected_slot})

@app.route("/uploadImages",methods = ['GET','POST'])
def toUploadImages():
    return render_template('uploadImages.html')

# @app.route("/processImages",methods = ['POST'])
# @login_required
# def processImages():
#     selected_day_str = request.form['selectedDay']
#     selected_day = datetime.strptime(selected_day_str, "%a %b %d %Y %H:%M:%S GMT%z (%Z)")  
#     selected_batch = request.form['selectedBatch']
#     selected_slot = request.form['selectedSlot']
#     if(selected_batch=="Lecture"):
#         selected_batch = "L"
#         current_attendance = markedAttendance(date = selected_day.date(), batch = 'L', slot = selected_slot)
#         print(selected_day.date())
#         existing = markedAttendance.query.filter_by(date=selected_day.date(), batch = 'L', slot = selected_slot).first()
#     else:
#         current_attendance = markedAttendance(date = selected_day.date(), batch = selected_batch, slot = selected_slot)
#         print(selected_day.date())
#         existing = markedAttendance.query.filter_by(date=selected_day.date(), batch = selected_batch, slot = selected_slot).first()
#     if not existing:
#         db.session.add(current_attendance)
#         db.session.commit()
#         known_face_encodings = joblib.load('known_face_encodings.joblib')
#         try:
#             # records_to_delete = AttendanceRecord.query.all()

#             # # Delete each record
#             # for record in records_to_delete:
#             #     db.session.delete(record)

#             # # Commit the changes to the database
#             # db.session.commit()
#             known_face_names = joblib.load('known_face_names.joblib')
#         except (Exception) as e:
#             print(f"Exception!: {e}")
#             known_face_names=[]
#         if 'images' in request.files:
#             uploaded_images = request.files.getlist('images')

#             for uploaded_image in uploaded_images:
#                 # Read the image from BytesIO
#                 image_data = uploaded_image.read()
#                 image = Image.open(BytesIO(image_data))
#                 print("Image received")
#                 np_image = np.array(image)

#                 # Find all face locations in the image using the 'hog' model
#                 face_locations = face_recognition.face_locations(np_image)
#                 face_encodings = face_recognition.face_encodings(np_image, face_locations)
#                 # Set a threshold for face recognition
#                 threshold = 0.4
#                 # Loop through each face found in the image
#                 for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#                     # Calculate distances between the current face and all known faces
#                     distances = face_recognition.face_distance(known_face_encodings, face_encoding)

#                     # Find the index with the smallest distance
#                     min_distance_index = distances.argmin()

#                     # Use the smallest distance to determine if it's a match
#                     if distances[min_distance_index] < threshold:
#                         print( distances[min_distance_index])
#                         roll_no = known_face_names[min_distance_index]
#                         student = Student.query.filter_by(roll_no=roll_no).first()

#                         if student:
#                             print(f"Name: {student.name}, Enrollment No: {student.enrollment_no}, Confidence: {1 - distances[min_distance_index]}")
#                             existing_record = AttendanceRecord.query.filter_by(date=datetime.now().date(), roll_no=roll_no,batch=selected_batch,slot=selected_slot).first()

#                             if not existing_record:
#                                 # If record doesn't exist, add a new record
#                                 new_attendance_record = AttendanceRecord(date=selected_day.date(), batch = selected_batch, slot = selected_slot,roll_no=roll_no, name=student.name,enrollment_no=student.enrollment_no, present='y')
#                                 db.session.add(new_attendance_record)
#                                 db.session.commit()
#                                 print("New attendance record added.")
#                             else:
#                                 print("Attendance record already exists.")
#                         else: 
#                             print("Student not found in the database.")
#                         print("Found: " + roll_no)
#                     else:
#                         roll_no = "Unknown"

#                     # Draw a rectangle around the face and display the name (optional)
#                     cv2.rectangle(np_image, (left, top), (right, bottom), (0, 255, 0), 2)
#                     cv2.putText(np_image, roll_no, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
#                     image_pil = Image.fromarray(np_image)
#                     image_pil.save('image.jpeg')

#                 # # Display the image with recognized faces (optional)
#                 # cv2.imshow('Face Recognition', np_image)
#                 # cv2.waitKey(0)
#                 # cv2.destroyAllWindows()
#     else:
#         print('Attendance already marked for the lecture!')
#         return 'AlreadyMarked'
#         #if record already exists
#     return 'Success'
    
@app.route("/fetchAttendance")
@login_required
def fetchAttendance():
    return render_template('fetchAttendance.html')

@app.route("/fetch_marked_attendance",methods = ['POST'])
@login_required
def handle_fetch_marked_attendance():
    try:   
        selected_day_str = request.form['selectedDay']
        selected_day = datetime.strptime(selected_day_str, "%a %b %d %Y %H:%M:%S GMT%z (%Z)")  
        print(selected_day.date())
        attendance_records = markedAttendance.query.filter_by(date=selected_day.date()).with_entities(markedAttendance.batch, markedAttendance.slot).all()
        unique_records = set((record.batch, record.slot) for record in attendance_records)
        print(unique_records)
        attendance_data = []
        for record in unique_records:
            attendance_data.append({
                'batch': record[0],
                'slot': record[1],
            })
            print(attendance_data)
        # result = AttendanceRecord.query.with_entities(AttendanceRecord.date, AttendanceRecord.subject, AttendanceRecord.batch).first()
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching attendance data'})
        return []
    return jsonify({'slots_batches': attendance_data})

# @app.route('/add_student', methods=['POST','GET'])
# def add_student():

#     if request.method == 'POST':  # Form Submitted
#         logging.basicConfig(filename='image_upload_debug.log', level=logging.DEBUG)
#         logging.debug(request.files) 
#         # Extract student info 
#         student_info = request.form.get('studentInfo')

#         if student_info:
#             roll_no = student_info.split(' - ')[0]  
#         else:
#             flash("Please select a student from the autocomplete list.")
#             return redirect(url_for('add_student'))

#         # Image Handling (Handles both uploads and individually sent captured images) 
#         if 'image-0' in request.files:
#             print("found captured images")  # Handle a single captured image
#             for i in range(5):  # Assuming you expect a maximum of 5
#                 key = f'image-{i}'  # Dynamic key for multiple captured images
#                 if key in request.files: 
#                     image_file = request.files[key]
#                     image_bytes = image_file.read()

#                     try:
#                         # Convert Blob to Image
#                         nparr = np.frombuffer(image_bytes, np.uint8)  
#                         image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#                         if image_cv2 is not None and not np.all(image_cv2 == 0): 
#                             image_pil = Image.fromarray(cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB))


#                             image_pil = process_image(image_pil)

#                             # Saving 
#                             filename = f'student_image_{roll_no}_{i}.jpg'  
#                             student_dir = os.path.join('training', str(roll_no))
#                             os.makedirs(student_dir, exist_ok=True)
#                             image_pil.save(os.path.join(student_dir, filename))  

#                         else:
#                             flash(f"Error processing captured image {i}: Unable to decode image.") 
#                     except Exception as e:
#                         flash(f"Error processing captured image {i}: {e}")

#             flash("Images saved successfully for existing student.")  
#             return redirect(url_for('add_student')) 

#         elif 'images' in request.files and request.files['images'].filename != '':
#             print("found uploaded image")  # Handle uploaded images (multiple at once)
#             images = request.files.getlist('images')
#             for image in images:
#                 if allowed_file(image.filename):
#                     filename = secure_filename(image.filename)
#                     student_dir = os.path.join('training', str(roll_no))
#                     os.makedirs(student_dir, exist_ok=True)
#                     image.save(os.path.join(student_dir, filename))
#                 else:
#                     flash(f"Invalid file format: {image.filename}") 

#         else:
#             flash("Please select images or capture a photo.")
#             return redirect(url_for('add_student'))

#     # GET Request Code (Displays the form)
#     return render_template('addStudent.html') 

@app.route('/upload_student_data', methods=['POST'])
def upload_student_data():
  if 'studentData' in request.files:
    student_data_file = request.files['studentData']
    df = pd.read_excel(student_data_file.stream)

    # Iterate through rows and add data to the 'students' table
    for index, row in df.iterrows():
      student = Student(
        roll_no=row['roll_no'],
        name=row['name'],
        enrollment_no=row['enrollment_no']
      )
      db.session.add(student)
    db.session.commit()

@app.route('/autocomplete')
def autocomplete():
    search_term = request.args.get('q')
    results = Student.query.filter(
        db.or_(
            Student.roll_no.like(f'%{search_term}%'),
            Student.name.like(f'%{search_term}%'),
            Student.enrollment_no.like(f'%{search_term}%')
        )
    ).all()

    data = [{
        'roll_no': student.roll_no,
        'name': student.name,
        'enrollment_no': student.enrollment_no
    } for student in results]

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)