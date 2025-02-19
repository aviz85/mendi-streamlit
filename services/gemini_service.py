import os
import google.generativeai as genai
from typing import Dict
import logging

class GeminiService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        
        # Configure Gemini
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction="לפניך טקסט מנוקד וטקסט עם פירוש לא מנוקד. קח את המקור המנוקד ותשכתב את הפירוש הלא מנוקד כאשר כל פעם שמופיע חלק מהמקור - תנקד. בפירוש בהתחלה מופיע כל הפסקה המלאה של המקור שיש לנקד, אח״כ מופיעים ביטויים חלקיים ופירוש, רק הביטויים החלקיים מהמקור יש לנקד."
        )
        
        self.chat_session = self.model.start_chat()
        self.logger.info("🤖 שירות Gemini אותחל")

    def add_nikud(self, content: Dict) -> str:
        """Process content through Gemini to add nikud"""
        self.logger.info(f"📝 מעבד חלק {content['target_header']} עם Gemini")
        
        prompt = f"""מקור:
{content['source_content']}

פירוש:
{content['target_content']}"""

        response = self.chat_session.send_message(prompt)
        
        self.logger.info(f"✅ עיבוד חלק {content['target_header']} הושלם")
        return response.text 