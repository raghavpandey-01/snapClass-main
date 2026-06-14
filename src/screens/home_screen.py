import streamlit as st

from src.components.header import home_header
from src.components.footer import footer_home

from src.ui.base_layout import style_base_layout,style_background_home,style_base_dashboard


def home_screen():
    
    home_header()
    style_background_home()
    style_base_layout()
    col1, col2 = st.columns(2,gap="large")



    with col1:
        st.markdown("""
            <h2> I'm </br> Student</h2>
        """, unsafe_allow_html=True)

        # st.header("I'm Student")
        st.image("https://static.vecteezy.com/system/resources/thumbnails/060/160/966/small/sumptuous-inspired-graduate-in-cap-and-gown-no-background-with-transparent-background-free-png.png",width=120)
        if st.button("Student portal ↗",  type= 'primary'):
            st.session_state['login_type'] = 'Student'
            st.rerun()

    with col2:
        st.header("I'm Teacher")
        st.image("https://static.vecteezy.com/system/resources/thumbnails/059/608/779/small/vibrant-artistic-teacher-explaining-lesson-enthusiastic-gesture-4k-free-png.png", width=120)
        if st.button("Teacher portal ↗", type= 'primary'):
            st.session_state['login_type'] = 'Teacher'
            st.rerun()
        
    footer_home()