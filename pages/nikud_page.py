import streamlit as st
import tempfile
import os
from services.nikud_service import NikudService
from services.usage_logger import streamlit_logger

def render_nikud_page():
    st.title("ניקוד אוטומטי")
    
    # Custom CSS for log display
    st.markdown("""
        <style>
            .log-container {
                background-color: #f0f2f6;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
                height: 400px;
                overflow-y: auto;
                direction: rtl;
            }
            .log-entry {
                padding: 5px 10px;
                margin: 2px 0;
                border-bottom: 1px solid #e0e0e0;
                font-family: monospace;
                white-space: nowrap;
            }
            .log-entry:hover {
                background-color: #e6e9ef;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        source_file = st.file_uploader("קובץ מקור (עם ניקוד)", type=["docx"])
        target_file = st.file_uploader("קובץ יעד (ללא ניקוד)", type=["docx"])
        
        if source_file and target_file:
            if st.button("התחל ניקוד", use_container_width=True):
                service = NikudService()
                
                # Save uploaded files
                with open("temp_source.docx", "wb") as f:
                    f.write(source_file.getvalue())
                with open("temp_target.docx", "wb") as f:
                    f.write(target_file.getvalue())
                
                # Process files
                service.process_files("temp_source.docx", "temp_target.docx", "output.docx")
                
                # Offer download
                with open("output.docx", "rb") as f:
                    st.download_button(
                        label="הורד קובץ מנוקד",
                        data=f.read(),
                        file_name="output.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
    
    with col2:
        log_container = st.container()
        with log_container:
            log_placeholder = st.empty()
            streamlit_logger.placeholder = log_placeholder
            streamlit_logger.clear()