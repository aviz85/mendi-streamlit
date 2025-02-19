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
            service = NikudService()
            
            # Save uploaded files
            with open("temp_source.docx", "wb") as f:
                f.write(source_file.getvalue())
            with open("temp_target.docx", "wb") as f:
                f.write(target_file.getvalue())
            
            # Get matches first
            matches = service.process_files("temp_source.docx", "temp_target.docx", "output.docx")
            
            if matches:
                st.write("### בחר פסקאות לניקוד")
                st.write("נמצאו ההתאמות הבאות בין המסמכים. סמן את הפסקאות שברצונך לנקד:")
                
                # Create checkboxes for each match
                selected_matches = []
                for match in matches:
                    if st.checkbox(f"{match['header']}", help=match['preview']):
                        selected_matches.append(match)
                
                if selected_matches:
                    if st.button("התחל ניקוד לפסקאות שנבחרו", use_container_width=True):
                        # Get target document sections and template
                        target_text, target_doc = service._read_docx("temp_target.docx")
                        target_sections = service.doc_processor.split_to_sections(target_text)
                        
                        # Process only selected sections
                        service.process_selected_sections(
                            selected_matches,
                            target_sections,
                            target_doc,
                            "output.docx"
                        )
                        
                        # Offer download
                        with open("output.docx", "rb") as f:
                            st.download_button(
                                label="הורד קובץ מנוקד",
                                data=f.read(),
                                file_name="output.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
            else:
                st.warning("לא נמצאו התאמות בין המסמכים")
    
    with col2:
        log_container = st.container()
        with log_container:
            log_placeholder = st.empty()
            streamlit_logger.placeholder = log_placeholder
            streamlit_logger.clear()