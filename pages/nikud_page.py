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
    
    # Initialize session state
    if 'nikud_service' not in st.session_state:
        st.session_state.nikud_service = NikudService()
    if 'processed_file' not in st.session_state:
        st.session_state.processed_file = None
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload with session state
        source_file = st.file_uploader("קובץ מקור (עם ניקוד)", type=["docx"], key="source_file")
        target_file = st.file_uploader("קובץ יעד (ללא ניקוד)", type=["docx"], key="target_file")
        
        if source_file and target_file:
            if st.button("התחל ניקוד", use_container_width=True, key="process_button"):
                with st.spinner('מעבד קבצים...'):
                    try:
                        output_data = process_files(st.session_state.nikud_service, source_file, target_file)
                        st.session_state.processed_file = output_data
                    except Exception as e:
                        st.error(f"שגיאה בעיבוד הקבצים: {str(e)}")
            
            # Show download button if we have processed file
            if st.session_state.processed_file is not None:
                st.download_button(
                    label="הורד קובץ מנוקד",
                    data=st.session_state.processed_file,
                    file_name="output.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    key="download_button"
                )
    
    with col2:
        log_container = st.container()
        with log_container:
            log_placeholder = st.empty()
            streamlit_logger.placeholder = log_placeholder
            # Only clear logs when starting new process
            if st.session_state.get('last_source') != source_file or st.session_state.get('last_target') != target_file:
                streamlit_logger.clear()
                st.session_state.last_source = source_file
                st.session_state.last_target = target_file