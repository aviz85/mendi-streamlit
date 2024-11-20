import streamlit as st
from services.state_manager import StateManager
from services.usage_logger import UsageLogger
from services.text_generator import create_interpretation_txt
from services.docx_generator import create_interpretation_docx
import io
from utils.interpretation import get_interpretation

def render_interpretation_page():
    # Initialize managers
    state_manager = StateManager()
    usage_logger = UsageLogger()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        user_text = st.text_area("הכנס טקסט לפירוש:", height=200)
        if st.button("פרש את הטקסט"):
            if not user_text:
                st.error("אנא הכנס טקסט לפירוש")
                return
                
            with st.spinner("מנתח את הטקסט..."):
                interpretation = get_interpretation(user_text)
                if interpretation:
                    state_manager.add_interpretation(interpretation)
                    with col2:
                        display_interpretation(interpretation)
    
    # Show history in sidebar
    with st.sidebar:
        st.title("היסטוריה")
        interpretations = state_manager.get_interpretations()
        
        for i, interp in enumerate(interpretations):
            with st.expander(f"פירוש {i+1}: {interp['original_text'][:20]}..."):
                st.write(f"**טקסט מקורי:** {interp['original_text']}")
                st.write(f"**אות:** {interp['letter']}")
                
                if st.button(f"טען פירוש {i+1}", key=f"load_{i}"):
                    with col2:
                        display_interpretation(interp)
        
        if interpretations:
            if st.button("נקה היסטוריה"):
                state_manager.clear()
                st.rerun()
        
        # Display usage statistics
        st.subheader("סטטיסטיקות שימוש")
        stats = usage_logger.get_usage_stats()
        
        st.metric("עלות כוללת", f"${stats['total_cost']:.4f}")
        st.metric("מספר קריאות", stats["calls_count"])
        st.metric("סה״כ טוקנים", f"{stats['total_tokens']:,}")
        
        if "per_model" in stats:
            st.subheader("שימוש לפי מודל")
            for model, model_stats in stats["per_model"].items():
                with st.expander(f"מודל: {model}"):
                    st.write(f"קריאות: {model_stats['calls']}")
                    st.write(f"טוקנים: {model_stats['total_tokens']:,}")
                    st.write(f"עלות: ${model_stats['cost']:.4f}")

def display_interpretation(interpretation):
    st.subheader("טקסט מקורי")
    st.write(interpretation["original_text"])
    
    st.subheader("אות")
    st.write(interpretation["letter"])
    
    st.subheader("מילים קשות")
    for word in interpretation["difficult_words"]:
        st.write(f"**{word['word']}**: {word['explanation']}")
    
    st.subheader("פירוש מפורט")
    for detail in interpretation["detailed_interpretation"]:
        st.write(f"**{detail['quote']}**: {detail['explanation']}")
        st.markdown("---")
    # Add download button
    doc = create_interpretation_docx(interpretation)
    bio = io.BytesIO()
    doc.save(bio)
    
    st.download_button(
        label="הורד כקובץ Word",
        data=bio.getvalue(),
        file_name="interpretation.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )