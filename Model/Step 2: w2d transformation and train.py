import pandas as pd
import os
import cv2
import numpy as np
import pywt
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.metrics import classification_report
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import joblib


# funtion to perform w2d transformation
def w2d(img, mode='haar', level=1):
    imArray = img
    # Convert to grayscale
    imArray = cv2.cvtColor(imArray, cv2.COLOR_BGR2GRAY)
    imArray = np.float32(imArray)
    imArray /= 255
    # Compute coefficients
    coeffs = pywt.wavedec2(imArray, mode, level=level)
    coeffs_H = list(coeffs)
    coeffs_H[0] *= 0
    # Reconstruct the image
    imArray_H = pywt.waverec2(coeffs_H, mode)
    imArray_H *= 255
    imArray_H = np.uint8(imArray_H)
    return imArray_H

# Define path
cropped_imgs_path = './dataset/cropped/'

# Load image directories
img_dirs = []
for entry in os.listdir(cropped_imgs_path):
    if os.path.isdir(os.path.join(cropped_imgs_path, entry)):
        img_dirs.append(entry)

# Dictionary to hold cropped images
cropped_images_dict = {}
for img_dir in img_dirs:
    cropped_images_dict[img_dir] = []

# Process each image directory
for img_dir in img_dirs:
    cropped_img_dir = os.path.join(cropped_imgs_path, img_dir)

    # Process each image in the directory
    for file_name in os.listdir(cropped_img_dir):
        cropped_images_dict[img_dir].append(os.path.join(cropped_img_dir, file_name))

# Print cropped images dictionary
# print('Cropped Images Dictionary:', cropped_images_dict)

# Create person to number mapping
person_to_num_dict = {person_name: idx for idx, person_name in enumerate(cropped_images_dict.keys())}
print('\nPerson to Number Mapping:')
for person, num in person_to_num_dict.items():
    print(f'{person}: {num}')
    
# x and y data preparation
x = []
y = []

# Process cropped images for feature extraction
for person_name, image_paths in cropped_images_dict.items():
    print(f'\nCropped images for {person_name}:')
    for img_path in image_paths:
        img = cv2.imread(img_path)
        scaled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img, 'haar', 5)
        scaled_har_img = cv2.resize(img_har, (32, 32))
        np_vertical = np.vstack((scaled_raw_img.reshape(32*32*3,1), scaled_har_img.reshape(32*32,1)))
        x.append(np_vertical)
        y.append(person_to_num_dict[person_name])
        
# Convert x array to numpy array
x = np.array(x).reshape(len(x), 32*32*3 + 32*32).astype(float)

# Split data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)

# # Define Model Params
# model_params = {
#     'svm': {
#         'model': SVC(gamma='auto', probability=True),
#         'params': {
#             'svc__C': [1, 10, 100, 1000],
#             'svc__kernel': ['rbf', 'linear']
#         }
#     },
#     'random_forest': {
#         'model': RandomForestClassifier(),
#         'params': {
#             'randomforestclassifier__n_estimators': [5, 10, 15],
#             'randomforestclassifier__criterion': ['gini', 'entropy']
#         }
#     },
#     'logistic_regression': {
#         'model': LogisticRegression(solver='liblinear', multi_class='ovr'),
#         'params': {
#             'logisticregression__C': [1, 5, 10]
#         }
#     }
# }

# # Calculate best model using GridSearchCV
# scores = []
# best_estimators = {}

# for model_name, mp in model_params.items():
#     pipe = make_pipeline(StandardScaler(), mp['model'])
#     clf = GridSearchCV(pipe, mp['params'], cv=5, return_train_score=False)
#     clf.fit(x_train, y_train)
#     scores.append({
#         'model': model_name,
#         'best_score': clf.best_score_,
#         'best_params': clf.best_params_
#     })
#     best_estimators[model_name] = clf.best_estimator_

# df = pd.DataFrame(scores, columns=['model', 'best_score', 'best_params'])
# print('\nBest Model Scores:')
# print(df)

# Already tested with GridSearchCV, directly using the best model (Logistic Regression with C=1)
best_model = make_pipeline(StandardScaler(), LogisticRegression(solver='liblinear', multi_class='ovr', C=1))
best_model.fit(x_train, y_train)

# Save the trained model
joblib.dump(best_model, 'best_model.joblib')

# Save person to num to json
import json
with open('person_to_num.json', 'w') as f:
    json.dump(person_to_num_dict, f)