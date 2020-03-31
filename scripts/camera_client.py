import face_recognition
import cv2
import requests
import cv2

import numpy as np
import cv2
import os

camera_id = os.getenv('CAMERA_ID')
DEBUG = False
RESET_THRESHOLD = 100
API_ENDPOINT = 'http://127.0.0.1:8000/camera_record/'
cap = cv2.VideoCapture(0)
process_this_frame = True

ct = 0
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    ct += 1
    ct = 0 if ct >= RESET_THRESHOLD else ct

    process_this_frame = True if i % 5 else False
    if process_this_frame:
        # Our operations on the frame come here
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Display the resulting frame
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame, model='cnn')
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        for i in range(len(face_encodings)):
            face_encodings[i] = face_encodings[i].tolist()
        if not DEBUG:
            data = {'face_encodings': face_encodings, 'camera_id': camera_id if camera_id else '0'}
            r = requests.post(url=API_ENDPOINT, json=data)
        elif DEBUG:
            for (top, right, bottom, left) in face_locations:
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, 'Test', (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
