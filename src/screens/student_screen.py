import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_home,footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendence
import time
from src.pipelines.face_pipeline import get_face_embeddings, train_model, get_trained_model
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import create_students,get_student_subjects,get_student_attendence, get_all_students, unenroll_student_to_subject
from src.components.enroll_dialog import enroll_dialog
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    c1,c2 = st.columns(2,vertical_alignment='center', gap = 'xxlarge')

    with c1:
        header_dashboard()
        if st.button("Home"):
            st.session_state["login_type"] = None
            st.rerun()

    with c2:
        st.subheader(f"W-{student_data['name']}")
        if st.button("Logout", type='secondary', key='logoutbtn', shortcut="control+backspace"):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()

    st.space()
    
    c1,c2 = st.columns(2)

    with c1:
        st.header("Enroll your Subject")
    with c2:
        if st.button("Enroll in your Subject" ,type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendence(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended":0}
            
        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] +=1
    
    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub_node['subject_id']

        stats = stats_map.get(sid, {"total":0, "attended":0} ) #we will get the sid:{total:..., attended:....} if nothing then we will return a fallback ({total:0, attended:0})
        
        def unenroll_button():
            if st.button("Unenroll from this subjects", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f"Unenrolled from {sub['name']}")

        with cols[i%2]:

            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats= [
                    ('🗓️ Total', stats['total']),
                    ('✅ Attended', stats['attended']),
                ],
                footer_callback = unenroll_button
            )

    footer_dashboard()

def student_screen():
    
    if st.session_state.get("is_logged_in") and st.session_state.get("user_role") == "student":
        student_dashboard()
        return

    c1,c2 = st.columns(2,vertical_alignment='center', gap = 'xxlarge')

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go to Home page", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state["login_type"] = None
            st.rerun()

    st.space()
    st.space()
    
    st.header('Login using FaceID', text_alignment='center')
    show_registeraion = False
    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning...'):
            detected, all_ids, num_faces =  predict_attendence(img)

            if num_faces == 0:
                st.warning('Face not found')
            elif num_faces > 1:
                st.warning('Multiple faces found')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_studetns = get_all_students()
                    student = next((s for s in all_studetns if s['student_id'] == student_id),None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"welcome back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('face not recognised1 you must be a new student ')
                    show_registeraion = True
    if show_registeraion:
        with st.container(border= True):
            st.header('Register new profile')
            new_name = st.text_input("Enter your name", placeholder='Raghav Pandey')

            st.subheader('Optional: Voice enrollement')
            st.info("Enroll for Voice only")

            audio_data = None

            try:
                audio_data = st.audio_input('Record a short phrase like I am present, My name is Raghav...')
            except Exception:
                st.error('Audio data error')

            if st.button('Create Account', type = 'primary'):
                if new_name:
                    with st.spinner('Creating profile'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_students(new_name, face_emb = face_emb, voice_emb = voice_emb)
                            
                            if response_data:
                                train_model()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile Created! Hi {new_name}')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Couldnt capture facial features for your registeration')



                else:
                    st.warning('Please enter your name first!!')
                    





    footer_dashboard()
