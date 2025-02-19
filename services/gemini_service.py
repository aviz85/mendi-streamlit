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
            system_instruction="""אתה מערכת טכנית לניקוד טקסט עברי. תפקידך הוא אך ורק:
1. לקחת טקסט מקור מנוקד וטקסט יעד לא מנוקד
2. לזהות את החלקים המודגשים בטקסט היעד (מסומנים בתגיות HTML: <b>טקסט מודגש</b>)
3. להעתיק את הניקוד מהמקור לחלקים המודגשים בלבד
4. להחזיר את הטקסט המלא עם הניקוד בחלקים המודגשים בלבד

חשוב:
- אל תוסיף פרשנות, הסברים או מקורות
- אל תשנה את הטקסט המקורי
- החזר רק את הטקסט עם הניקוד בחלקים המודגשים
- שמור על תגיות ה-HTML (<b></b>) במקומן המדויק

דוגמה:
מקור: בְּרֵאשִׁית בָּרָא אֱלֹהִים
יעד: פירוש על <b>בראשית</b> ועל <b>ברא</b> בתורה
פלט: פירוש על <b>בְּרֵאשִׁית</b> ועל <b>בָּרָא</b> בתורה"""
        )
        
        self.chat_session = self.model.start_chat()
        st_log.log("שירות Gemini מוכן", "✅")

    def add_nikud(self, content: Dict) -> str:
        """Process content through Gemini to add nikud"""
        st_log.log(f"מעבד חלק: {content['target_header']}", "📝")
        
        prompt = f"""מקור (עם ניקוד):
{content['source_content']}

טקסט לניקוד (יש לנקד רק את הטקסט בין תגיות <b></b>):
{content['target_content']}

הנחיות:
- נקד רק טקסט בין תגיות <b></b>
- השאר את התגיות <b></b> במקומן בדיוק
- אל תשנה טקסט שאינו בין התגיות
- התאם את הניקוד למקור
- החזר רק את הטקסט המנוקד, ללא הסברים או מקורות"""

        st_log.log("שולח בקשה ל-Gemini...", "🔄")
        response = self.chat_session.send_message(prompt)
        st_log.log(f"התקבלה תשובה מ-Gemini", "✨")
        
        return response.text 