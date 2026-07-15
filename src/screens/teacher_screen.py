import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_home,footer_dashboard
from src.database.db import check_teacher_exist, create_teacher,teacher_login, get_teacher_subjects
from src.components.dialog_create_subject import create_subject_dialog
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photos import add_photos_dialog
from src.components.dialog_attendence_result import attendence_result_dialog
import numpy as np
from PIL import Image
from src.pipelines.face_pipeline import predict_attendence
from src.database.config import supabase
import time
from datetime import datetime
import pandas as pd
from src.components.dialog_voice_attendence import voice_attendence_dialog
from src.database.db import get_attendence_for_teacher
def teacher_screen():

    style_base_layout()
    style_background_dashboard()
    
    if 'teacher_data' in st.session_state:
        teacher_dashboard()

    elif 'teacher_login_type' not in st.session_state or st.session_state["teacher_login_type"]=="login":
        teacher_screen_login()

    elif st.session_state["teacher_login_type"]=="register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data

    c1,c2 = st.columns(2,vertical_alignment='center', gap = 'xxlarge')

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"""" Welcome {teacher_data['name']}""")
        if st.button("Logout", type='secondary', key='logoutbtn', shortcut="control+backspace"):
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()
    
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendence'
    tab1, tab2, tab3 = st.columns(3)
 
    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "take_attendence" else "tertiary"
        if st.button('Take Attedence',type=type1, width='stretch'):
            st.session_state.current_teacher_tab = 'take_attendence'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
        if st.button('Manage subjects',type=type2, width='stretch'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
    

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendence_records" else "tertiary"
        if st.button('Attendence records',type=type3, width='stretch'):
            st.session_state.current_teacher_tab = 'attendence_records'
            st.rerun()
    
    st.divider()

    if st.session_state.current_teacher_tab == 'take_attendence':
        teacher_tab_take_attendence()
    
    if st.session_state.current_teacher_tab == 'manage_subjects':
        teacher_tab_manage_subjects()

    if st.session_state.current_teacher_tab == 'attendence_records':
        teacher_tab_attendence_records()


def teacher_tab_take_attendence():

#     """"
# Teacher opens page
#         ↓
# Load teacher's subjects
#         ↓
# Teacher selects a subject
#         ↓
# Teacher uploads classroom photos
#         ↓
# Photos are displayed
#         ↓
# Teacher clicks Run Face Analysis
#         ↓
# AI recognizes students
#         ↓
# Compare with enrolled students
#         ↓
# Mark Present/Absent
#         ↓
# Show result dialog
#         ↓
# Save attendance
# """"
    
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header("Take AI attendece")

    if 'attendence_images' not in st.session_state:
        st.session_state.attendence_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning("You have'nt created any subjects yet! Please create one")
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}" : s['subject_id'] for s in subjects}

    # {
    #     "Java-CS101":1,
    #     "Python-CS102":2
    # }

    col1, col2 = st.columns([3,1],vertical_alignment="bottom")

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options= list(subject_options.keys()))

    with col2:
        if st.button('🖼️ Add photos', type='primary',width = 'stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]
    
    
    
    if st.session_state.attendence_images:
        st.header('Added photos')
        img_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendence_images):
            with img_cols[idx%4]:
                st.image(img,width='stretch', caption=f"Photo{idx+1}")
                
    has_photos = bool(st.session_state.attendence_images)
    st.divider()

    c1, c2, c3 =  st.columns(3)

    with c1:
        if st.button('❌ Clear photos',  width='stretch',type='tertiary',disabled=not has_photos):
            st.session_state.attendence_images.clear()
            st.rerun()

    with c2:
            if st.button('📷 Analyze Faces', width="stretch", type='secondary',disabled=not has_photos):
                with st.spinner('Deep scanning classroom photos...'):
                    all_detected_id = {}

                    for idx, img in enumerate(st.session_state.attendence_images):
                        img_np = np.array(img.convert('RGB'))
                        detected, _, _ = predict_attendence(img_np)

                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)

                                all_detected_id.setdefault(student_id,[]).append(f"Photo {idx+1}")

                    enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                    enrolled_students = enrolled_res.data

                    if not enrolled_students:
                        st.warning("No students enrolled in this course")
                    else:                                                        
                        results, attenedence_to_log = [],[]

                        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                        for node in enrolled_students:
                            student = node['students']
                            sources = all_detected_id.get(int(student['student_id']), []) #subject me enrolled students ki id detected_students wali dict me dal ke check krenge ki kisi photo source me available hai ki nhi,
                            is_present = len(sources) > 0 # agr kisi photo source me available nhi hai toh empty lis return hogi or is_present False ho jayga

                            #jo attendence_result display hoga->
                            results.append({
                                "Name": student['name'],
                                "ID": student['student_id'],
                                "Source": ",".join(sources) if is_present else "-",
                                "Status": "✅ Present" if is_present else "❌ Absent"
                            })

                            # jo attendence log me save ho jayga->
                            attenedence_to_log.append({
                                'student_id':student['student_id'],
                                'subject_id': selected_subject_id,
                                'time_stamp': current_timestamp,
                                'is_present': bool(is_present)
                            })

                    attendence_result_dialog(pd.DataFrame(results), attenedence_to_log)

    with c3:
        if st.button('Voice attendence', type='primary', width='stretch', icon=":material/mic:"):
            voice_attendence_dialog(selected_subject_id)
            

    st.divider()
    
def teacher_tab_manage_subjects():
   
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)

    with col1:
        st.header("Manage your subjects",width='stretch')

    with col2:
        if st.button("Create new subject",width='stretch'):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects( teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ( "👥Students", sub["total_students"]), 
                ( "⏱️Classes", sub["total_classes"]),
            ]
        
            def share_btn():
                if st.button(f"Share code: {sub['name']}", key=f"share_{'subject_code'} ➦" ):
                    share_subject_dialog(sub['name'], sub['subject_code'])
                st.space()


            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats=stats,
                footer_callback = share_btn
            )
    else :
        st.info("No subjects found. Create your subjects first")


def teacher_tab_attendence_records():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header("Attendence records")
    records = get_attendence_for_teacher(teacher_id)

    if not records:
        return
    
    data = []
    for r in records:
        ts = r.get('time_stamp')

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N'A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))

        })

    df = pd.DataFrame(data)

    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present','sum'),
            Total_Count = ('is_present', 'count')
        ).reset_index()   
    )

    summary['Attendence Stats'] = (
        "✅"+summary['Present_Count'].astype(str)+"/"+summary['Total_Count'].astype(str)+ 'Students'
    )

    display_df = (summary.sort_values(by='ts_group', ascending=False)
                    [['Time', 'Subject', 'Subject Code', 'Attendence Stats']]
                    )

    st.dataframe(display_df, width='stretch', hide_index=True)

def register_teacher(teacher_username, teacher_name,teacher_pass, teacher_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required"
    
    if check_teacher_exist(teacher_username):
        return False, "Username already exists"
    
    if teacher_pass != teacher_confirm:
        return False, "Password doesn't match"

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Succesfully Created! Login Now"
    except Exception as e:
        return False, "Unexpeected error!"


def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    
    else:
        False

def teacher_screen_login():
    c1,c2 = st.columns(2,vertical_alignment='center', gap = 'xxlarge')

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go to Home page", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state["login_type"] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder='@raghav')
    
    teacher_pass = st.text_input("Enter password", type="password" ,placeholder="****")

    st.divider()
    
    btnc1, btnc2 = st.columns(2,gap="xxlarge")

    with btnc1:
       if st.button('Login',width='stretch', shortcut="control+enter"):
           if login_teacher(teacher_username,teacher_pass):
               st.toast("Welcome back", icon="👋")
        # pop-up is done with st.toast()
               import time
               time.sleep(1)
               st.rerun()
              
           else:
               st.error("Invalid Username or Password")
               
               

    with btnc2:
        if st.button('Register instead',type='primary',width='stretch',shortcut="control+enter"):
            st.session_state['teacher_login_type'] = "register"

    footer_dashboard()
  
def teacher_screen_register():
    c1,c2 = st.columns(2,vertical_alignment='center', gap = 'xxlarge')

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go to Home page", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state["login_type"] = None
            st.rerun()
    
    st.header("Register your teacher profile")
    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder='@raghav')
    
    teacher_name = st.text_input("Enter name", placeholder='Raghav Pandey')
    
    teacher_pass = st.text_input("Enter password", type="password" ,placeholder="****")
    
    teacher_confirm = st.text_input("Confirm password", type="password" ,placeholder="****", key="confirm_pass")

    st.divider()
    
    btnc1, btnc2 = st.columns(2,gap="xxlarge")

    with btnc1:
        if st.button('Login page',width='stretch', shortcut="control+enter"):
            st.session_state['teacher_login_type'] = 'login'

    with btnc2:
        if st.button('Register now',type='primary',width='stretch',shortcut="control+enter"):
            success, message = register_teacher(teacher_username, teacher_name,teacher_pass, teacher_confirm)

            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state["teacher_login_type"] = "login"
                st.rerun()
            else:
                st.error(message)

    footer_dashboard()
    