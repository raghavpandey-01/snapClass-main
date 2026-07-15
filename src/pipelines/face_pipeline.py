import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students

@st.cache_resource #this ensures the model loads only once in the system.
def load_dlib_models():
    
    # finds where the faces are in the image (just like the esp box in )
    face_detector = dlib.get_frontal_face_detector()
    
    #finds facial landmarks(eyes, nose, jaw inside the detected face box)
    # just as the skelton
    shape_detector = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    
    #turns the align face into a 128-dim vector
    face_recog = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return face_detector, shape_detector, face_recog

 
def get_face_embeddings(image_np):
    face_detector, shape_detector, face_recog = load_dlib_models()

    faces = face_detector(image_np,1) #. The 1 is the "upsample" factor — it enlarges the image once before scanning, which helps detect smaller/farther-away faces.
     
    encodings=[] #store the encoding(128vec as a face) of every face in the image

    for face in faces:
        shape = shape_detector(image_np, face) #har boxed face ka landmark bnayega
        #sare faces ke landmarks bna ke fir unki embedding lelo
        face_descriptor = face_recog.compute_face_descriptor(image_np, shape,1) #The trailing 1 is num_jitters — it resamples the face slightly and averages multiple embeddings for more robustness 

        encodings.append(np.array(face_descriptor)) #sare face ki encodings ko store kr do 
    return encodings

@st.cache_resource
def get_trained_model():
    X = []
    Y = []

    student_db = get_all_students()

    if not student_db:
        return None
    
    for student in student_db: #get every student from database
        embedding = student.get('face_embedding') #get their respective face-embeddings
        if embedding:
            X.append(np.array(embedding)) #store the embeddings in X for training
            Y.append(student.get('student_id')) #and student's respective id in Y for results(predictions)

    if len(X) == 0: #mtlb koi bhi student ni tha database me
        return None
    #model ko initialize krna hai
    model = SVC(kernel='linear', probability=True, class_weight='balanced')

    try:
        model.fit(X,Y) #fit/train the model on the given x,y data
    except ValueError:
        return None

    return {'model':model,'X':X,'Y':Y} #return the model and x,y data

#to train with the new database clear all the old model that is trained on the old db 
def train_model(): 
    st.cache_resource.clear()
    model_data = get_trained_model() #get the results,x and y from the above function
    return bool(model_data)

def predict_attendence(class_image_np):
    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return {}, [], len(encodings) #num of students, students_list, len(encodings) 
    
    model = model_data['model']
    X_train = model_data['X']
    Y_train = model_data['Y']

    all_students = sorted(list(set(Y_train)))

    for encoding in encodings:
        if len(all_students)>=2:
            predicted_id = int(model.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])
        #The predicted postion in the y_train is the exact position of the X_train embedding(basically to get the exact position of the embeddig)
        student_embedding = X_train[Y_train.index(predicted_id)]
        #jo id model ne predict ki hai us id ka embedding ko current encoding se comapre krna ki shi predicted hai ki nhi
        best_match_score = np.linalg.norm(student_embedding - encoding)

        resemblance_threshold = 0.6

        if best_match_score <= resemblance_threshold:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(encodings)