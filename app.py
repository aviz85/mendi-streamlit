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
                context=INTERPRETATION_EXAMPLES,
                user_text=text
            )
        }]
    )
    
    # Extract JSON from response
    try:
        response_text = message.content[0].text
        # Find JSON part between ```json and ```
        json_start = response_text.find('```json\n') + 8
        json_end = response_text.find('```', json_start)
        json_str = response_text[json_start:json_end].strip()
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Failed to parse response: {e}")
        return None

def main():
    st.title("Text Interpretation Assistant")
    st.write("Enter a text passage to receive a structured interpretation")
    
    user_text = st.text_area("Enter text to interpret:", height=200)
    
    if st.button("Interpret"):
        if user_text:
            with st.spinner("Analyzing..."):
                interpretation = get_interpretation(user_text)
                
                if interpretation:
                    st.subheader("Main Themes")
                    for theme in interpretation["main_themes"]:
                        st.write(f"**{theme['theme']}**")
                        st.write(theme["explanation"])
                    
                    st.subheader("Literary Devices")
                    for device in interpretation["literary_devices"]:
                        st.write(f"**{device['device']}**")
                        st.write(f"Example: {device['example']}")
                        st.write(f"Effect: {device['effect']}")
                    
                    st.subheader("Deeper Meaning")
                    st.write(interpretation["deeper_meaning"])
                    
                    if interpretation.get("historical_context"):
                        st.subheader("Historical Context")
                        st.write(interpretation["historical_context"])
                    
                    st.subheader("Key Insights")
                    for insight in interpretation["key_insights"]:
                        st.write(f"• {insight}")
        else:
            st.error("Please enter some text to interpret")

if __name__ == "__main__":
    main() 