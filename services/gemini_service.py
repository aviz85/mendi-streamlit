import os
import google.generativeai as genai
from typing import Dict
import logging
from .usage_logger import streamlit_logger as st_log

class GeminiService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        
        st_log.log("מאתחל את שירות Gemini...", "🔄")
        
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
            system_instruction="""אתה מערכת לניקוד טקסט עברי. תפקידך:
1. לקחת טקסט מקור מנוקד וטקסט יעד לא מנוקד
2. לזהות את החלקים המודגשים בטקסט היעד (מסומנים ב-**)
3. להוסיף ניקוד רק לחלקים המודגשים, תוך התאמה לניקוד במקור
4. להשאיר את שאר הטקסט ללא שינוי
5. לשמור על הסימון ** סביב החלקים המודגשים

דוגמה:
מקור: בְּרֵאשִׁית בָּרָא אֱלֹהִים
יעד: פירוש על **בראשית** ועל **ברא** בתורה
פלט: פירוש על **בְּרֵאשִׁית** ועל **בָּרָא** בתורה"""
        )
        
        self.chat_session = self.model.start_chat()
        st_log.log("שירות Gemini מוכן", "✅")

    def add_nikud(self, content: Dict) -> str:
        """Process content through Gemini to add nikud"""
        st_log.log(f"מעבד חלק: {content['target_header']}", "📝")
        
        prompt = f"""מקור (עם ניקוד):
{content['source_content']}

טקסט לניקוד (יש לנקד רק את החלקים המודגשים ב-**):
{content['target_content']}

שים לב:
- נקד רק טקסט בין ** **
- השאר את סימני ** במקומם
- אל תשנה טקסט שאינו מודגש
- התאם את הניקוד למקור"""

        st_log.log("שולח בקשה ל-Gemini...", "🔄")
        response = self.chat_session.send_message(prompt)
        st_log.log(f"התקבלה תשובה מ-Gemini", "✨")
        
        return response.text 