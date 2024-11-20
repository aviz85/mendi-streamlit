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
    
    # Initialize usage logger
    usage_logger = UsageLogger()
    
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
    
    # Log usage after getting response
    usage_logger.log_usage(
        model_name=message.model,
        usage=message.usage
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