import face_recognition
import requests

import cv2

API_ENDPOINT = 'http://127.0.0.1:8000/register_user/'
DEBUG = True

# basic info input
while True:
    name = input('Enter full name: ')
    email = input('Enter email:')
    identity = name + email
    print(f'Name: {name} | Email: {email}')
    correct = input('Info correct?')
    if not name or not email:
        print('Empty name or email input is invalid, please re-try!')
        continue
    if correct.lower() == 'y':
        break


# collect face encoding data
person_face_encodings = []
while True:
    print('Start capture face data! Press "Y" for accepting a capture!')
    cap = cv2.VideoCapture(0)
    # Capture frame-by-frame
    i = 0
    while i < 30:
        ret, frame = cap.read()
        i += 1
    print(frame.shape)
    cap.release()

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
    print(len(face_encodings))
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

    while True:
        cv2.imshow('capture image and face demo', frame)  # display the captured image
        if cv2.waitKey(1) & 0xFF == ord('y'):  # save on pressing 'y'
            cv2.destroyAllWindows()
            break


    choose = input('Face OK? (Y/N) ')
    if choose.lower() == 'y' and len(face_encodings) == 1:
        person_face_encodings.extend(face_encodings)

    another = input('Get another face capture data? (Y/N) ')
    if another.lower() == 'y':
        continue
    elif another.lower() == 'n':
        break


print(f'For user {name} with email address {email}, we have collected {len(person_face_encodings)} face(s).')
print(f'Creating new user (updating user info if exist)...')
data = {'face_encodings': face_encodings,
        'name': name, 'email': email, 'identity': identity}

r = requests.post(url=API_ENDPOINT, json=data)
print(r.status_code, type(r.status_code))
