import streamlit as st
import tempfile
import os
from services.nikud_mapper import NikudMapper
from services.nikud_service import NikudService
from services.usage_logger import streamlit_logger

def render_nikud_page():
    st.title("ניקוד אוטומטי")
    
    # Create placeholder for logs
    log_placeholder = st.empty()
    streamlit_logger.placeholder = log_placeholder
    
    # Clear previous logs
    streamlit_logger.clear()
    
    # File upload
    source_file = st.file_uploader("קובץ מקור (עם ניקוד)", type=["docx"])
    target_file = st.file_uploader("קובץ יעד (ללא ניקוד)", type=["docx"])
    
    if source_file and target_file:
        if st.button("התחל ניקוד"):
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
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

def show():
    st.title("ניקוד אוטומטי")
    
    # Create placeholder for logs
    log_placeholder = st.empty()
    streamlit_logger.placeholder = log_placeholder
    
    # Clear previous logs
    streamlit_logger.clear()
    
    # File upload
    source_file = st.file_uploader("קובץ מקור (עם ניקוד)", type=["docx"])
    target_file = st.file_uploader("קובץ יעד (ללא ניקוד)", type=["docx"])
    
    if source_file and target_file:
        if st.button("התחל ניקוד"):
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
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )