"""
Document Processor App

A Streamlit application for processing and analyzing documents.
The app provides the following features:
- Document upload and processing
- Analysis of document structure and content
- Preview of processed documents
- Download of processed documents
"""

import os
import tempfile
import streamlit as st
from typing import Optional

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_processor import DocumentProcessor
from services.usage_logger import streamlit_logger as st_log

# Set page configuration
st.set_page_config(
    page_title="Document Processor",
    page_icon="📄",
    layout="wide"
)

# Initialize document processor
processor = DocumentProcessor()

# App title and description
st.title("מעבד מסמכים חכם")
st.markdown("""
יישום לעיבוד וניתוח מסמכים עם זיהוי אוטומטי של מבנה הסעיפים
""")

# File upload section
uploaded_file = st.file_uploader("העלאת מסמך Word (DOCX)", type=["docx"])

# Processor sidebar
with st.sidebar:
    st.header("אפשרויות עיבוד")
    
    # Processing options
    st.checkbox("זיהוי אוטומטי של סעיפים", value=True, disabled=True)
    st.checkbox("שמירה על עיצוב מקורי", value=True, disabled=True)
    
    # Action buttons (enabled only when file is uploaded)
    process_btn = st.button("עיבוד המסמך", disabled=not uploaded_file)
    
    # Log section
    st.header("יומן פעולות")
    logs_container = st.container()
    
    # Clear logs button
    if st.button("ניקוי יומן פעולות"):
        st_log.clear_logs()
    
    def update_logs():
        """Update log display in sidebar"""
        with logs_container:
            st_log.display_logs(st)

# Process document function
def process_document(file_bytes) -> Optional[dict]:
    """
    Process an uploaded document
    
    Parameters:
        file_bytes: The uploaded file bytes
        
    Returns:
        Processing results or None if an error occurred
    """
    try:
        # Create a temporary file for the uploaded content
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        
        # Create a temporary file for the output
        output_path = temp_path + "_processed.docx"
        
        # Process the document
        result = processor.process_document(temp_path, output_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return result
    except Exception as e:
        st.error(f"שגיאה בעיבוד המסמך: {str(e)}")
        st_log.log(f"שגיאה בעיבוד המסמך: {str(e)}", "❌")
        return None

# Main app flow
if uploaded_file and process_btn:
    # Show processing message
    with st.spinner("מעבד את המסמך..."):
        # Process the document
        result = process_document(uploaded_file.getvalue())
        update_logs()
    
    # If processing was successful
    if result and not "error" in result:
        st.success("המסמך עובד בהצלחה!")
        
        # Display document statistics
        st.header("מידע על המסמך")
        stats = result["stats"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("מספר פסקאות", stats["paragraphs_count"])
        with col2:
            st.metric("מספר סעיפים", stats["sections_count"])
        with col3:
            st.metric("מקטעים מודגשים", stats["bold_segments"])
        
        # Display document preview
        st.header("תצוגה מקדימה")
        
        # Create HTML preview
        preview_html = processor.create_preview(result["sections"])
        
        # Display the preview using HTML
        st.markdown(preview_html, unsafe_allow_html=True)
        
        # Download button for processed file
        output_file = result.get("output_file")
        if output_file and os.path.exists(output_file):
            with open(output_file, "rb") as file:
                file_bytes = file.read()
                
            st.download_button(
                label="הורדת המסמך המעובד",
                data=file_bytes,
                file_name=f"processed_{uploaded_file.name}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            # Clean up the temporary output file
            os.unlink(output_file)
        
    # If there was an error
    elif result and "error" in result:
        st.error(result["error"])
        
# Display logs in sidebar
update_logs()

# Custom CSS for RTL support and styling
st.markdown("""
<style>
    body {
        direction: rtl;
    }
    .css-18e3th9, .css-1d391kg {
        direction: rtl;
    }
    h1, h2, h3, h4, h5, h6, p, div {
        text-align: right;
    }
    .document-preview {
        border: 1px solid #ccc;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 5px;
        margin-bottom: 20px;
        direction: rtl;
    }
    .section-header {
        margin-top: 10px;
        font-weight: bold;
    }
    .section-content {
        margin-bottom: 10px;
        line-height: 1.5;
    }
    .section-children {
        margin-right: 20px;
        padding-right: 10px;
        border-right: 2px solid #e0e0e0;
    }
    .section-article {
        color: #1a5276;
    }
    .section-chapter {
        color: #117a65;
    }
    .doc-title {
        font-size: 1.5em;
        text-align: center;
        margin-bottom: 20px;
        color: #34495e;
    }
</style>
""", unsafe_allow_html=True) 