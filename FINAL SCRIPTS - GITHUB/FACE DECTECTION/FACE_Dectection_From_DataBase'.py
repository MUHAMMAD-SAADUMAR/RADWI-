import os
import pickle
import firebase_admin
from datetime import datetime
import numpy as np
import cv2
import face_recognition
import time
from firebase_admin import credentials, db, storage


def initialize_firebase(cred_path, db_url, storage_bucket):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': db_url,
        'storageBucket': storage_bucket
    })


def fetch_images_and_encodings():
    ref = db.reference('Known_faces')
    data = ref.get()
    encode_list = []
    names = []

    for key, value in data.items():
        names.append(key)
        encodings = value.get('encodings')
        encode_list.append(np.array(encodings))

    return encode_list, names


def recognize_faces_in_frame(frame, known_face_encodings, known_face_names):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_recognized = False
    recognized_name = ""
    face_location_scaled = None

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

        if True not in matches:
            continue

        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            recognized_name = known_face_names[best_match_index]
            face_recognized = True
            face_location_scaled = [coord * 4 for coord in face_location]  # Scale face location back

            break

    return face_recognized, recognized_name, face_location_scaled


def main():
    # Initialize Firebase
    initialize_firebase("privateKey.json", "https://realtimefaceidentification-default-rtdb.firebaseio.com/",
                        "realtimefaceidentification.appspot.com")

    # Fetch images and encoded data from Firebase
    print("Fetching Encode Data from Firebase...")
    encodeListKnown, nameOfKnownPeople = fetch_images_and_encodings()
    print("Encode Data Fetched")

    # Open the webcam
    # cap = cv2.VideoCapture("rtsp://admin:InLights@192.168.110.233/Streaming/channels/1?tcp&buffer_size=102400")
    cap = cv2.VideoCapture("http://0.0.0.0/video")
    cap.set(3, 640)
    cap.set(4, 480)

    start_time = None
    identified_flag = False

    while True:
        success, img = cap.read()
        if not success:
            break

        face_recognized, recognized_name, face_location = recognize_faces_in_frame(img, encodeListKnown,
                                                                                   nameOfKnownPeople)

        if face_recognized:
            top, right, bottom, left = face_location
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(img, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, recognized_name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            if identified_flag:
                elapsed_time = time.time() - start_time
                if elapsed_time >= 3:
                    print(f"Verified as {recognized_name}")
                    ref = db.reference(f'Known_faces/{recognized_name}')
                    ref.child('last_verification_time').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    studentInfo = db.reference(f'Known_faces/{recognized_name}/last_verification_time').get()
                    print('last_verification_time  : ', studentInfo)

                    identified_flag = False
                    start_time = None
            else:
                identified_flag = True
                start_time = time.time()
        else:
            identified_flag = False
            start_time = None

        cv2.imshow('Video', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
