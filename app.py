import streamlit as st
import anthropic
import json
from prompt_template import SYSTEM_PROMPT, PROMPT_TEMPLATE
from examples import INTERPRETATION_EXAMPLES
from services.text_generator import create_interpretation_txt
from services.docx_generator import create_interpretation_docx
import io
import re

def get_interpretation(text):
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    model_name = st.secrets["MODEL_NAME"]
    client = anthropic.Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model=model_name,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user", 
            "content": PROMPT_TEMPLATE.format(
                text_to_analyze=text
            )
        }]
    )
    
    # Extract JSON from response using regex
    try:
        response_text = message.content[0].text
        
        # Try to find JSON between code blocks first
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback: try to find any JSON object
            json_match = re.search(r'\{(?:[^{}]|(?R))*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No JSON found in response")
        
        # Clean up any potential markdown artifacts
        json_str = re.sub(r'\\n', '\n', json_str)
        json_str = json_str.strip()
        
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Failed to parse response: {e}")
        st.write("Raw response:", response_text)  # Debug output
        return None

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
    
    # Initialize session state for interpretation
    if 'interpretation' not in st.session_state:
        st.session_state.interpretation = None
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        user_text = st.text_area("הכנס טקסט לפירוש:", height=200)
        if st.button("פרש את הטקסט"):
            if not user_text:
                st.error("אנא הכנס טקסט לפירוש")
                return
                
            with st.spinner("מנתח את הטקסט..."):
                st.session_state.interpretation = get_interpretation(user_text)
    
    # Display interpretation if exists
    if st.session_state.interpretation:
        with col2:
            st.subheader("טקסט מקורי")
            st.write(st.session_state.interpretation["original_text"])
            
            st.subheader("אות")
            st.write(st.session_state.interpretation["letter"])
            
            st.subheader("מילים קשות")
            for word in st.session_state.interpretation["difficult_words"]:
                st.write(f"**{word['word']}**: {word['explanation']}")
            
            st.subheader("פירוש מפורט")
            for detail in st.session_state.interpretation["detailed_interpretation"]:
                st.write(f"**ציטוט**: {detail['quote']}")
                st.write(f"**פירוש**: {detail['explanation']}")
                st.markdown("---")
            
            # Create docx file in memory
            doc = create_interpretation_docx(st.session_state.interpretation)
            bio = io.BytesIO()
            doc.save(bio)
            
            st.download_button(
                label="הורד כקובץ Word",
                data=bio.getvalue(),
                file_name="interpretation.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

if __name__ == "__main__":
    main() 