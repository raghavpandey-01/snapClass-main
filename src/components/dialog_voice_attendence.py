import streamlit as st
from src.pipelines.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.dialog_attendence_result import show_attendence_results
@st.dialog('Voice Attendence')

def voice_attendence_dialog(sub_id):
    st.write('Record sudio of students saying "I am present"')

    audio_data = None

    audio_data = st.audio_input("Record classroom audio")

    if st.button('Analyze Audio', width='stretch', type='primary'):
        with st.spinner('Processig your audio'):
            enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', sub_id).execute()
            enrolled_students = enrolled_res.data
            # this is enrolled students data structure
            #  [
            #     {
            #         "subject_id":101,
            #         "student_id":1,
            #         "students":{
            #             "student_id":1,
            #             "name":"Raghav",
            #             "face_embedding":[...],
            #             "voice_embedding":[...]
            #         }
            #     },

            #     {
            #         "subject_id":101,
            #         "student_id":2,
            #         "students":{
            #             "student_id":2,
            #             "name":"Aman",
            #             "face_embedding":[...],
            #             "voice_embedding":[...]
            #         }
            #     }
            # ] 

            # if traversing this is how a node looks like
            # {
            #     "subject_id":101,
            #     "student_id":1,

            #     "students":{
            #         "student_id":1,
            #         "name":"Raghav",
            #         "face_embedding":[...],
            #         "voice_embedding":[...]
            #     }
            # }

            #from here we can do like node['students'] -> for getting all the students table data ->

            if not enrolled_students:
                st.warning('No students enrolled in this course')
                return
            
            candidates_dict = {
                s['students']['student_id'] : s['students']['voice_embedding']
                for s in enrolled_students if s['students'].get('voice_embedding')
            }

            if not candidates_dict:
                st.error('No enrolled students have voice profile registered')
                return
            
            audio_bytes = audio_data.read()

            detected_scores = process_bulk_audio(audio_bytes, candidates_dict)

            results, attendence_to_log = [], []
            
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score =  detected_scores.get(student['student_id'],0.0)
                is_present = (score) > 0

                results.append({
                    "Name":student['name'],
                    "ID": student['student_id'],
                    "Source": score if is_present else "-",
                    "Status": "✅Present" if is_present else "❌Absent"
                })

                attendence_to_log.append({
                    'student_id': student['student_id'],
                    'subject_id': sub_id,
                    'time_stamp': current_timestamp,
                    'is_present' : bool(is_present)
                })

            st.session_state.voice_attendence_results = (pd.DataFrame(results), attendence_to_log)

    if st.session_state.voice_attendence_results:
        st.divider()
        df_results,  logs  = st.session_state.voice_attendence_results
        show_attendence_results(df_results, logs)
        



