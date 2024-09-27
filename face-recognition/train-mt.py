import cv2 as cv
import os
import numpy as np
from mtcnn.mtcnn import MTCNN
from keras_facenet import FaceNet
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle

class FaceRecognitionTrainer:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.target_size = (160, 160)
        self.detector = MTCNN()
        self.embedder = FaceNet()
        self.encoder = LabelEncoder()
        self.model = SVC(kernel='linear', probability=True)

    def extract_face(self, filename):
        img = cv.imread(filename)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        result = self.detector.detect_faces(img)
        if result:
            x, y, w, h = result[0]['box']
            x, y = abs(x), abs(y)
            face = img[y:y+h, x:x+w]
            face_arr = cv.resize(face, self.target_size)
            return face_arr
        else:
            raise ValueError("No face found in the image.")

    def load_faces(self, dir):
        faces = []
        for im_name in os.listdir(dir):
            try:
                path = os.path.join(dir, im_name)
                single_face = self.extract_face(path)
                faces.append(single_face)
            except Exception as e:
                print(f"Error processing {im_name}: {e}")
        return faces

    def load_dataset(self):
        X = []
        Y = []
        for subdir in os.listdir(self.dataset_path):
            path = os.path.join(self.dataset_path, subdir)
            faces = self.load_faces(path)
            labels = [subdir for _ in range(len(faces))]
            print(f'Loaded successfully: {len(labels)} samples for {subdir}')
            X.extend(faces)
            Y.extend(labels)

        return np.asarray(X), np.asarray(Y)

    def generate_embeddings(self, X):
        embedded_X = []
        for img in X:
            img = img.astype('float32')
            img = np.expand_dims(img, axis=0)
            yhat = self.embedder.embeddings(img)
            embedded_X.append(yhat[0])

        return np.asarray(embedded_X)

    def train_model(self, X, Y):
        self.encoder.fit(Y)
        Y_encoded = self.encoder.transform(Y)
        X_train, _, Y_train, _ = train_test_split(X, Y_encoded, test_size=0.2, random_state=42)

        self.model.fit(X_train, Y_train)
        print("Model trained successfully.")

    def save_model_and_embeddings(self, embedded_X, Y):
        with open("svm_model.pkl", 'wb') as model_file:
            pickle.dump(self.model, model_file)

        np.savez_compressed('faces_embeddings.npz', embedded_X, Y)
        print("Model and embeddings saved successfully.")

    def save_embeddings(self, embeddings_path):
        try:
            print("Loading dataset...")
            X, Y = self.load_dataset()
            print("Generating embeddings...")
            X = self.generate_embeddings(X)
            print("Saving embeddings...")
            
            with open(embeddings_path, 'wb') as f:
                pickle.dump((X, Y), f)  # Save both embeddings and labels
                
            print(f"Embeddings saved to {embeddings_path}")
        except Exception as e:
            print(f"An error occurred while saving embeddings: {e}")

# Example of how to use the class
# trainer = FaceRecognitionTrainer('path_to_your_dataset')
# trainer.save_embeddings('faces_embeddings.pkl')
