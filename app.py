import streamlit as st
import anthropic
import json
from prompt_template import SYSTEM_PROMPT, PROMPT_TEMPLATE
from examples import INTERPRETATION_EXAMPLES

def get_interpretation(text):
    api_key = st.secrets["ANTHROPIC_API_KEY"]
    client = anthropic.Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user", 
            "content": PROMPT_TEMPLATE.format(
                text_to_analyze=text
            )
        }]
    )
    
    # Extract JSON from response
    try:
        response_text = message.content[0].text
        json_start = response_text.find('```json\n') + 8
        json_end = response_text.find('```', json_start)
        json_str = response_text[json_start:json_end].strip()
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Failed to parse response: {e}")
        return None

def main():
    # Set page config and CSS
    st.set_page_config(layout="wide")
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap');
            
            .stApp {
                direction: rtl;
                font-family: 'Heebo', sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .stTextArea textarea {
                direction: rtl;
                font-family: 'Heebo', sans-serif;
                font-size: 18px;
                padding: 15px;
                border-radius: 10px;
                width: 100%;
            }
            
            .stButton button {
                font-family: 'Heebo', sans-serif;
                font-size: 18px;
                padding: 10px 30px;
                border-radius: 20px;
                background-color: #1f77b4;
                color: white;
                border: none;
                width: 100%;
                margin: 20px 0;
            }
            
            .interpretation-box {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border: 1px solid #eee;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            h1, h2, h3 {
                color: #2c3e50;
                font-family: 'Heebo', sans-serif;
                font-weight: 700;
                text-align: center;
                margin: 20px 0;
            }
            
            .header-section {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .content-section {
                max-width: 900px;
                margin: 0 auto;
            }
        </style>
    """, unsafe_allow_html=True)

    # Title and description in centered header section
    st.markdown("""
        <div class='header-section'>
            <h1>מנדי - עוזר אישי לכתיבת פירוש תורני</h1>
            <h3>הכנס קטע טקסט לניתוח ופירוש מעמיק</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Content section with max-width
    st.markdown("<div class='content-section'>", unsafe_allow_html=True)
    
    # Create two columns with adjusted ratios
    col1, col2 = st.columns([1, 1])
    
    with col1:
        user_text = st.text_area("הכנס טקסט לפירוש:", height=200)
        if st.button("פרש את הטקסט", use_container_width=True):
            if not user_text:
                st.error("אנא הכנס טקסט לפירוש")
                return
                
            with st.spinner("מנתח את הטקסט..."):
                interpretation = get_interpretation(user_text)
                
                if interpretation:
                    with col2:
                        # Original text
                        st.markdown("""
                            <div class='interpretation-box'>
                                <h3>טקסט מקורי</h3>
                                <p>{}</p>
                            </div>
                        """.format(interpretation["original_text"]), unsafe_allow_html=True)
                        
                        # Letter
                        st.markdown("""
                            <div class='interpretation-box'>
                                <h3>אות</h3>
                                <p>{}</p>
                            </div>
                        """.format(interpretation["letter"]), unsafe_allow_html=True)
                        
                        # Difficult words
                        difficult_words_html = "<div class='interpretation-box'><h3>מילים קשות</h3>"
                        for word in interpretation["difficult_words"]:
                            difficult_words_html += f"<p><strong>{word['word']}</strong>: {word['explanation']}</p>"
                        difficult_words_html += "</div>"
                        st.markdown(difficult_words_html, unsafe_allow_html=True)
                        
                        # Detailed interpretation
                        detailed_html = "<div class='interpretation-box'><h3>פירוש מפורט</h3>"
                        for detail in interpretation["detailed_interpretation"]:
                            detailed_html += f"""
                                <div style='margin-bottom: 20px;'>
                                    <p><strong>ציטוט:</strong> {detail['quote']}</p>
                                    <p><strong>פירוש:</strong> {detail['explanation']}</p>
                                    <hr style='margin: 10px 0;'>
                                </div>
                            """
                        detailed_html += "</div>"
                        st.markdown(detailed_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 