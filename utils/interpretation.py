import streamlit as st
import anthropic
import json
import re
from services.usage_logger import UsageLogger
from prompt_template import SYSTEM_PROMPT, PROMPT_TEMPLATE

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
    
    # Log usage
    try:
        usage = {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens
        }
        usage_logger = UsageLogger()
        usage_logger.log_usage(
            model_name=message.model,
            usage=usage
        )
    except Exception as e:
        print(f"Usage logging error: {e}")
    
    # Parse response
    try:
        response_text = message.content[0].text
        
        # Extract JSON from code block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.MULTILINE)
        
        if not json_match:
            # Try without json tag
            json_match = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.MULTILINE)
            
        if not json_match:
            # Try raw JSON
            json_match = re.search(r'\{[^{]*"letter":[^{]*"original_text":[^}]*\}', response_text, re.DOTALL)
            
        if json_match:
            json_str = json_match.group(1)
            # Clean up newlines and spaces
            json_str = re.sub(r'\s+', ' ', json_str).strip()
            return json.loads(json_str)
            
        st.error("לא נמצא פלט תקין מהמודל. אנא נסה שנית.")
        print("Raw response:", response_text)
        return None
    except Exception as e:
        st.error(f"Failed to parse response: {e}")
        st.write("Raw response:", response_text)  # Debug output
        return None