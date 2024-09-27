import cv2
import sys
import numpy as np
import os

size = 4
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'trained_faces'
print('Recognizing Face. Please ensure sufficient lighting...')

# Create a list of images and a list of corresponding labels (ids)
(images, labels) = ([], [])

# Create a dictionary to map label ids to names
id_to_name = {}

# Load the pre-trained LBPH face recognizer
model = cv2.face.LBPHFaceRecognizer_create()

# Traverse through the dataset directory to collect images and labels
for (subdirs, dirs, files) in os.walk(datasets):
    for subdir in dirs:
        subject_path = os.path.join(datasets, subdir)
        id_to_name[len(id_to_name)] = subdir
        for filename in os.listdir(subject_path):
            path = os.path.join(subject_path, filename)
            label = len(id_to_name) - 1  # Assign the label (id) based on the order in id_to_name dictionary
            image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                images.append(image)
                labels.append(label)

# Train the LBPH face recognizer
model.train(images, np.array(labels))

# Part 2: Use LBPH Face Recognizer on camera stream
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
webcam = cv2.VideoCapture(0)
width=100
height=100
while True:
    ret, im = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        
        # Try to recognize the face
        label, confidence = model.predict(face_resize)
        if confidence <90:  # You may need to adjust this threshold
            recognized_name = id_to_name[label]
            cv2.putText(im, recognized_name, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
        else:
            cv2.putText(im, 'Not Recognized', (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))

    cv2.imshow('OpenCV', im)

    key = cv2.waitKey(10)
    if key == 27:
        break

webcam.release()
cv2.destroyAllWindows()

