import os
import pickle
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, storage, db
import face_recognition
import numpy as np


# Initialize Firebase
cred = credentials.Certificate("privateKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https:///',
    'storageBucket': ''
})

# Known person's images directory
known_persons_dir = 'Known_faces'

def upload_data_to_firebase():
    known_face_encodings = []
    known_face_names = []

    # Iterate through the subdirectories in the known persons directory
    for person_name in os.listdir(known_persons_dir):
        person_dir = os.path.join(known_persons_dir, person_name)
        if os.path.isdir(person_dir):
            # Initialize encodings list for current person
            person_encodings = []

            # Iterate through each image file for the current person
            for filename in os.listdir(person_dir):
                if filename.endswith('.jpg') or filename.endswith('.png'):
                    try:
                        # Load the image file
                        image_path = os.path.join(person_dir, filename)
                        image = face_recognition.load_image_file(image_path)

                        # Encode the face
                        face_encodings = face_recognition.face_encodings(image)
                        if face_encodings:
                            person_encodings.extend(face_encodings)

                        # Upload the file to Firebase storage
                        bucket = storage.bucket()
                        blob = bucket.blob(f'{person_name}/{filename}')
                        blob.upload_from_filename(image_path)

                    except Exception as e:
                        print(f"Error processing file {image_path}: {e}")

            # Add all encodings for current person to the list
            if person_encodings:
                known_face_encodings.extend(person_encodings)
                known_face_names.extend([person_name] * len(person_encodings))

    # print("known_face_encodings : " , known_face_encodings )
    # print("known_face_names : " , known_face_names )


    # Save the encodings and names to a file
    with open('EncodeFile.p', 'wb') as file:
        pickle.dump([known_face_encodings, known_face_names], file)

    # Upload the encodings to Firebase Realtime Database
    encode_data = {
        name: {
            'encodings': encoding.tolist(),
            'name': name,
            'last_verification_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        for name, encoding in zip(known_face_names, known_face_encodings)
    }
    db.reference('Known_faces').set(encode_data)

    print("Encodings and names saved to EncodeFile.p and uploaded to Firebase")

# Call the function to upload data to Firebase
upload_data_to_firebase()
