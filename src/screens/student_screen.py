import streamlit as st

def student_screen():
    st.header("Student screen")

    if st.button("Home"):
        st.session_state['login_type'] = None
        st.rerun()