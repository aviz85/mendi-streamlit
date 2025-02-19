import os
import google.generativeai as genai
from typing import Dict
import logging
import sys
from .usage_logger import streamlit_logger as st_log

def setup_logger():
    """Setup detailed logging to both file and console"""
    logger = logging.getLogger('GeminiService')
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler('gemini_service.log')
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

class GeminiService:
    def __init__(self):
        self.logger = setup_logger()
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
1. לקבל טקסט מקור מנוקד (החלק העיקרי בלבד)
2. לקבל סקשן שלם של טקסט יעד (כולל כותרת וכל התוכן)
3. להחזיר את הסקשן במלואו, בדיוק כפי שהוא, עם שני שינויים בלבד:
   א. להעתיק את הניקוד מהמקור לחלקים המודגשים בלבד (בין תגיות <b></b>)
   ב. להשאיר את שאר הטקסט ללא ניקוד

חשוב מאוד:
- העתק את כל הסקשן במדויק, מילה במילה
- אל תשנה שום דבר מלבד הוספת ניקוד לחלקים המודגשים
- שמור על כל תגיות ה-HTML (<b></b>) במקומן המדויק
- אל תוסיף ואל תסיר שום תגית
- אל תשנה את סדר המילים או התוכן

דוגמה:
[מקור]
בְּרֵאשִׁית בָּרָא אֱלֹהִים

[סקשן יעד]
פרק א
פירוש על <b>בראשית</b> ועל <b>ברא</b> בתורה
הסבר נוסף כאן...

[פלט]
פרק א
פירוש על <b>בְּרֵאשִׁית</b> ועל <b>בָּרָא</b> בתורה
הסבר נוסף כאן..."""
        )
        
        self.chat_session = self.model.start_chat()
        st_log.log("שירות Gemini מוכן", "✅")

    def add_nikud(self, content: Dict) -> str:
        """Process content through Gemini to add nikud"""
        st_log.log(f"מעבד חלק: {content['target_header']}", "📝")
        
        prompt = f"""[טקסט מקור (עם ניקוד) - החלק העיקרי]:
{content['source_content']}

[סקשן יעד מלא - יש לשכתב במדויק עם ניקוד בחלקים המודגשים בלבד]:
{content['target_content']}

הנחיות חשובות:
1. העתק את כל הסקשן הנ"ל במדויק, מילה במילה
2. הוסף ניקוד רק לטקסט שנמצא בין תגיות <b></b>
3. השאר את כל שאר הטקסט בדיוק כפי שהוא
4. שמור על כל תגיות ה-HTML במקומן המדויק
5. החזר את הסקשן המלא בדיוק כפי שהוא, עם ניקוד רק בחלקים המודגשים"""

        # Log full prompt with clear separators
        self.logger.info("\n" + "="*50 + "\nFULL GEMINI PROMPT:\n" + "="*50 + "\n" + prompt)
        
        st_log.log("שולח בקשה ל-Gemini...", "🔄")
        response = self.chat_session.send_message(prompt)
        
        # Log full response with clear separators
        self.logger.info("\n" + "="*50 + "\nFULL GEMINI RESPONSE:\n" + "="*50 + "\n" + response.text)
        
        st_log.log(f"התקבלה תשובה מ-Gemini", "✨")
        
        return response.text 