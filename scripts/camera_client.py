import face_recognition
import cv2
import requests
import cv2

cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, image = cap.read()
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    known_encodings = []
    known_names = []

    # detect the (x, y)-coordinates of the bounding boxes
    # corresponding to each face in the input image
    boxes = face_recognition.face_locations(rgb,
        model='cnn')
    # compute the facial embedding for the face
    encodings = face_recognition.face_encodings(rgb, boxes)
    print(len(encodings))