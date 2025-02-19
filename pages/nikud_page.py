import streamlit as st
import tempfile
import os
from services.nikud_service import NikudService
from services.usage_logger import streamlit_logger

def process_files(service: NikudService, source_file, target_file):
    """Process the uploaded files with proper temp file handling"""
    # Create temp files with unique names
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as source_temp:
        source_temp.write(source_file.getvalue())
        source_path = source_temp.name
        
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as target_temp:
        target_temp.write(target_file.getvalue())
        target_path = target_temp.name
        
    output_path = os.path.join(tempfile.gettempdir(), 'output.docx')
    
    try:
        # Process the files
        service.process_files(source_path, target_path, output_path)
        
        # Read the output file
        with open(output_path, 'rb') as f:
            output_data = f.read()
            
        return output_data
        
    finally:
        # Clean up temp files
        for path in [source_path, target_path, output_path]:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                st.error(f"Error cleaning up temp file {path}: {str(e)}")

def render_nikud_page():
    st.title("ניקוד אוטומטי")
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        source_file = st.file_uploader("קובץ מקור (עם ניקוד)", type=["docx"])
        target_file = st.file_uploader("קובץ יעד (ללא ניקוד)", type=["docx"])
        
        if source_file and target_file:
            if st.button("התחל ניקוד", use_container_width=True):
                service = NikudService()
                
                with st.spinner('מעבד קבצים...'):
                    try:
                        output_data = process_files(service, source_file, target_file)
                        
                        st.download_button(
                            label="הורד קובץ מנוקד",
                            data=output_data,
                            file_name="output.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"שגיאה בעיבוד הקבצים: {str(e)}")
    
    with col2:
        log_container = st.container()
        with log_container:
            log_placeholder = st.empty()
            streamlit_logger.placeholder = log_placeholder
            streamlit_logger.clear()