import streamlit as st
from config import GLOBAL_CSS

def init_streamlit():
    """Initialize Streamlit configuration and styling"""
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="collapsed",
        page_title="מנדי - עוזר אישי לכתיבת פירוש תורני",
        page_icon="📚"
    )
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def main():
    # Initialize Streamlit first
    init_streamlit()
    
    # Then import page modules to avoid premature Streamlit commands
    from pages.nikud_page import render_nikud_page
    from pages.interpretation_page import render_interpretation_page
    from pages.logs_page import render_logs_page
    
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