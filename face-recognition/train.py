import os
import face_recognition
import joblib

def train_face_recognition_model(data_path):
    known_face_encodings = []
    known_face_names = []

    for person in os.listdir(data_path):
        person_path = os.path.join(data_path, person)
        for img_file in os.listdir(person_path):
            img_path = os.path.join(person_path, img_file)
            image = face_recognition.load_image_file(img_path)

            # Check if any faces are detected in the image
            face_locations = face_recognition.face_locations(image)
            if len(face_locations) == 0:
                print(f"No faces found in {img_path}")
                continue

            # Take the first face encoding (assuming only one face is present)
            face_encoding = face_recognition.face_encodings(image, [face_locations[0]], num_jitters=70)[0]

            known_face_encodings.append(face_encoding)
            known_face_names.append(person)

    # Save the trained model
    joblib.dump(known_face_encodings, 'known_face_encodings.joblib')
    joblib.dump(known_face_names, 'known_face_names.joblib')

    print("Training completed successfully.")

# Replace 'path/to/training_data' with the actual path to your training dataset
train_data_path = 'training'
train_face_recognition_model(train_data_path)
