import streamlit as st
from pages.nikud_page import render_nikud_page
from pages.interpretation_page import render_interpretation_page
from pages.logs_page import render_logs_page

def main():
    # Set basic page config
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="collapsed",
        page_title="מנדי - עוזר אישי לכתיבת פירוש תורני",
        page_icon="📚"
    )
    
    # Minimal CSS just for RTL support
    st.markdown("""
        <style>
            .stApp { direction: rtl; }
            .stTextArea textarea { direction: rtl; }
        </style>
    """, unsafe_allow_html=True)

    st.title("מנדי - עוזר אישי לכתיבת פירוש תורני")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["פירוש תורני", "ניקוד אוטומטי", "סטטיסטיקות"])
    
    with tab1:
        render_interpretation_page()
    
    with tab2:
        render_nikud_page()
        
    with tab3:
        render_logs_page()

if __name__ == "__main__":
    main() 