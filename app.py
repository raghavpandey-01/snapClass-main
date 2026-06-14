import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.student_screen import student_screen

def main(): #defining the function
#     st.header("This is the header")
#     name = st.text_input('Enter your name')
    
#     col1, col2 = st.columns(2,gap="medium")
#     with col1:
#         if st.button('click me',type='primary' ):
#             print('Hi i am', name)

#     with col2:
#         st.button('click me', type='secondary')
#         st.button('click me', type='secondary', key='btn2')

#     with col1:
#         st.button('click me', type='tertiary')

#     st.markdown("""
#       **This is bold**

#       1. item1
#       2. item2
#       3. item3

#       'Heloow'

#     """)   

#     st.markdown("""   
#       <div>
#         <h1>Snap Class web app</h1>           
#         <p>This is a paragraph</p>       
#       </div>
                
# """,unsafe_allow_html=True)
    
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'Teacher':
            teacher_screen()

        case 'Student':
            student_screen()       
            
        case None:
            home_screen()    

main() # calling the main funtion