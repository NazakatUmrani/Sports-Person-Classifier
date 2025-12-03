import json
import joblib
import numpy as np
import cv2
from wavelet import w2d
import base64

__num_to_person = None
__person_to_num = None
__model = None

def get_num_to_person():
    return __num_to_person

# Function to load saved artifacts
def load_saved_artifacts():
    print("Loading saved artifacts...")
    
    global __num_to_person
    global __person_to_num
    global __model
    
    with open("./artifacts/person_to_num.json", "r") as f:
        __person_to_num = json.load(f)
        __num_to_person = {v: k for k, v in __person_to_num.items()}

    with open("./artifacts/best_model.joblib", "rb") as f:
        __model = joblib.load(f)
    print("Artifacts loaded successfully.")

# Function to crop image if 2 eyes are detected
def get_cropped_image_if_2_eyes(image_base64):
    # Decode base64 image
    nparr = np.frombuffer(base64.b64decode(image_base64.split(',')[1]), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # load haar cascade for face and eye detection
    face_cascade = cv2.CascadeClassifier('./artifacts/opencv/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('./artifacts/opencv/haarcascades/haarcascade_eye.xml')
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    cropped_faces = []
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            cropped_faces.append(roi_color)
    return cropped_faces

# Function to classify image
def classify_image(image_base64):
    cropped_faces = get_cropped_image_if_2_eyes(image_base64)
    if len(cropped_faces) == 0:
        return "No face with 2 eyes detected."
    
    results = []
    for face in cropped_faces:
        scalled_raw_img = cv2.resize(face, (32, 32))
        img_har = w2d(scalled_raw_img, 'db1', 5)
        scalled_har_img = cv2.resize(img_har, (32, 32))
        combined_img = np.vstack((scalled_raw_img.reshape(32*32*3, 1), scalled_har_img.reshape(32*32, 1)))
        
        combined_img = combined_img.reshape(1, 32*32*3 + 32*32).astype(float)
        predicted_num = __model.predict(combined_img)[0]
        results.append({
            "class": __num_to_person[predicted_num],
            "class_probability": np.round(__model.predict_proba(combined_img) * 100, 2).tolist()[0],
        })
    
    return results

# Check if image is base64 encoded
def is_base64(image_base64):
    try:
        base64.b64decode(image_base64.split(',')[1])
        return True
    except Exception:
        return False

if __name__ == "__main__":
    load_saved_artifacts()
    print(classify_image(""))  # Add a valid base64 image string for testing
    