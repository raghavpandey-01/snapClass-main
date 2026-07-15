import streamlit as st

def style_background_home():
    st.markdown("""

  <style>
        .stApp{
            background:  #5865F2 !important;
        }
                
        .stApp div[data-testid = "stColumn"]{
                background-color: #E0E3FF !important;
                padding: 2.5rem !important;
                border-radius: 5rem !important;
                max-width: 320px !important;
                max-height: 340px !important;
        }
  </style>

    """,unsafe_allow_html=True)

def style_background_dashboard():
    st.markdown("""

  <style>
        .stApp{
            background:  #E0E3FF !important;
        }
  </style>

    """,unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""

  <style>
                
    @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&family=Outfit:wght@100..900&display=swap');
                             
       #MainMenu, footer, header{
                visibility: hidden;
        }
                
        .block-container{
                padding-top:1.5rem !important;
               
        }
        
        input{
                margin-top: 0px !important;
                width: 665px !important;
                border:none !important;
                border-radius:0.4rem !important;
                padding-left:10px !important;
                
        }
        h1{
            
            font-family: 'Climate Crisis', sans-serif !important;
            font-size : 3.5rem !important;
            line-height:1.1 !important;
            margin-bottom:0rem !important;
            color: #E0E3FF !important;
        }
        
        .head{
            font-size: 2.5rem !important;    
        }
                
        h2{
            font-family: 'Climate Crisis', sans-serif !important;
            font-size: 2rem !important;
            line-height: 0.9 !important;
            margin-bottom:0rem !important;
        } 

        .dash{
               font-size: 1.7rem !important; 
        }         

        .register{
                margin-top:0px !important;
                padding-top:0px !important;
                margin-bottom:50px !important;
        }      
        h3,h4,p{
                font-family: 'Outfit', sans-serif;
        }

        button[kind="primary"]{
            border-radius: 1.5rem !important;
            background: #5865F2 !important;
            color: white !important;
            padding: 10px 20px !important;
            border: none !important;
            transition: transform 0.25s ease-in-out !important;
        }   
        button[kind="secondary"]{
            border-radius: 1.5rem !important;
            background: #EB459E !important;
            color: white !important;
            padding: 10px 20px !important;
            border: none !important;
            transition: transform 0.25s ease-in-out !important;
        }
        
        button[kind="tertiary"]{
            border-radius: 1.5rem !important;
            background: black !important;
            color: white !important;
            padding: 10px 20px !important;
            border: none !important;
            transition: transform 0.25s ease-in-out !important;
        }
                
        button:hover{
                transform: scale(1.06)
            }
  </style>

    """,unsafe_allow_html=True)    