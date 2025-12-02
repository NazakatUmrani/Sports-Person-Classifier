import os
import cv2
import shutil

# function to return cropped Image
def get_cropped_image_if_2_eyes(image_path):
    # Load the image from the specified path
    img = cv2.imread(image_path)
    print(f'Image shape: {img.shape}')

    eye_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_eye.xml')
    face_cascade = cv2.CascadeClassifier('./opencv/haarcascades/haarcascade_frontalface_default.xml')
    
    # Convert the image to grayscale and detect faces
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    face_images = []
    
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        
        # Detect eyes within the face region
        eyes = eye_cascade.detectMultiScale(roi_gray)
        print(f'Eyes found: {len(eyes)}')
        if len(eyes) >= 2:
            face_images.append(roi_color)
            
    return face_images

# Define paths
data_path = './dataset/'
cropped_imgs_path = './dataset/cropped/'

# Load image directories
img_dirs = []
for entry in os.listdir(data_path):
    if os.path.isdir(os.path.join(data_path, entry)):
        img_dirs.append(entry)

# Prepare cropped images directory
if os.path.exists(cropped_imgs_path):
    shutil.rmtree(cropped_imgs_path)
os.makedirs(cropped_imgs_path)

# Process each image directory
for img_dir in img_dirs:
    count = 1
    img_path = os.path.join(data_path, img_dir)
    cropped_img_dir = os.path.join(cropped_imgs_path, img_dir)
    os.makedirs(cropped_img_dir)
    
    # Process each image in the directory
    for file_name in os.listdir(img_path):
        image_path = os.path.join(img_path, file_name)
        cropped_images = get_cropped_image_if_2_eyes(image_path)
        for cropped_image in cropped_images:
            save_path = os.path.join(cropped_img_dir, f'image_{str(count)}.jpg')
            cv2.imwrite(save_path, cropped_image)
            print(f'Cropped image saved to: {save_path}')
            count += 1          