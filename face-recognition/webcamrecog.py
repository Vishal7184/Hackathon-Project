
import cv2
import os

# Path to the Haar cascade file
haar_file = 'haarcascade_frontalface_default.xml'

# Directory for storing face data
datasets = 'trained_faces'  

# Subfolder for this specific individual's face
sub_data = 'Shreyash Chilip'     
path = os.path.join(datasets, sub_data)

# Create the subfolder if it doesn't exist
if not os.path.isdir(path):
    os.makedirs(path)

# Defining the size of the images
(width, height) = (130, 100)    

# Using '0' for the default webcam
face_cascade = cv2.CascadeClassifier(haar_file)
webcam = cv2.VideoCapture(0) 

# The program loops until it has 50 images of the face.
count = 1
while count <= 50: 
    # Capture frame-by-frame
    ret, im = webcam.read()
    if not ret:
        print("Failed to capture image. Exiting...")
        break
    
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 4)
    
    # Draw rectangle around the faces and save the images
    for (x, y, w, h) in faces:
        cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        cv2.imwrite(os.path.join(path, f'{count}.png'), face_resize)
        count += 1  # Increment the count after saving an image

    cv2.imshow('OpenCV', im)
    
    # Break the loop on 'Esc' key press
    key = cv2.waitKey(10)
    if key == 27:  # ASCII value of 'Esc' key
        break

# Release the webcam and close windows
webcam.release()
cv2.destroyAllWindows()
