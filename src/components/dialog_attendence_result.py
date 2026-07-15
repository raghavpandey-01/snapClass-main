import streamlit as st
from src.database.config import supabase
import time
from src.database.db import create_attendence

def show_attendence_results(df, logs):
    st.write('Please review attendence before confirming.')
    st.dataframe(df, hide_index=True, width='stretch')

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard', width='stretch'):
            st.session_state.voice_attendence_results = None
            st.session_state.attendence_images = []
            st.rerun()

    with col2:
        if st.button('confirm & save', width='stretch',type='primary'):
            try:
                create_attendence(logs)
                st.toast('Attendence taken')
                st.session_state.attendence_images = []
                st.session_state.voice_attendence_results = None
                st.rerun()
                
            except Exception as e:
                st.error(f'Sync failed: {e}')

@st.dialog("Attendence Reports")
def attendence_result_dialog(df, logs):
    show_attendence_results(df, logs)