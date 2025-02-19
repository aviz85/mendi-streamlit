import streamlit as st
import tempfile
import os
from services.nikud_mapper import NikudMapper

def render_nikud_page():
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        source_file = st.file_uploader(
            "העלה קובץ מקור מנוקד (Word)",
            type=['docx'],
            key="source_nikud"
        )
        
        input_file = st.file_uploader(
            "העלה קובץ לניקוד (Word)",
            type=['docx'],
            key="input_nikud"
        )
        
        if st.button("בצע ניקוד אוטומטי"):
            if not source_file or not input_file:
                st.error("יש להעלות את שני הקבצים")
                return
                
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save uploaded files
                    source_path = os.path.join(temp_dir, "source.docx")
                    input_path = os.path.join(temp_dir, "input.docx")
                    output_path = os.path.join(temp_dir, "output.docx")
                    
                    with open(source_path, 'wb') as f:
                        f.write(source_file.getvalue())
                    with open(input_path, 'wb') as f:
                        f.write(input_file.getvalue())
                    
                    # Process files
                    with st.spinner("מבצע ניקוד אוטומטי..."):
                        mapper = NikudMapper(bold_only=True)
                        mapper.process_docx(input_path, output_path, source_path)
                    
                    # Read output file
                    with open(output_path, 'rb') as f:
                        output_data = f.read()
                    
                    # Store in session state for download
                    st.session_state.nikud_output = output_data
                    st.session_state.show_nikud_download = True
                    
                    st.success("הניקוד הושלם בהצלחה!")
                    
            except Exception as e:
                st.error(f"אירעה שגיאה בעיבוד הקבצים: {str(e)}")
    
    with col2:
        st.subheader("קובץ מנוקד")
        if st.session_state.get('show_nikud_download', False):
            st.download_button(
                label="הורד קובץ מנוקד",
                data=st.session_state.nikud_output,
                file_name="output_nikud.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )