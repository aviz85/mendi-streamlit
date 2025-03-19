import os
import google.generativeai as genai
from typing import Dict
import logging
import sys
from .usage_logger import streamlit_logger as st_log
import streamlit as st

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
    def __init__(self, api_key: str = None):
        self.logger = setup_logger()
        
        # Try to get API key from different sources
        if api_key:
            self.api_key = api_key
        else:
            try:
                self.api_key = st.secrets["GEMINI_API_KEY"]
            except:
                self.api_key = os.environ.get("GEMINI_API_KEY")
                
        if not self.api_key:
            raise ValueError("No Gemini API key provided")
            
        genai.configure(api_key=self.api_key)
        
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
   א. להעתיק את הניקוד מהמקור לכל החלקים המודגשים (בין תגיות <b></b>)
   ב. להשאיר את שאר הטקסט ללא ניקוד

חשוב מאוד:
- העתק את כל הסקשן במדויק, מילה במילה
- כל טקסט מודגש (בין תגיות <b></b>) חייב לקבל ניקוד מלא
- אל תשנה שום דבר מלבד הוספת ניקוד לחלקים המודגשים
- שמור על כל תגיות ה-HTML (<b></b>) במקומן המדויק
- אל תוסיף תגיות <br> או כל תגית HTML אחרת
- אל תשנה את סדר המילים או התוכן
- טקסט שאינו בין תגיות <b></b> חייב להישאר ללא ניקוד, אפילו אם הוא זהה לטקסט מנוקד במקור

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

    def add_nikud(self, content: Dict, report_path: str = None) -> str:
        """Process content through Gemini to add nikud"""
        st_log.log(f"מעבד חלק: {content['target_header']}", "📝")
        
        prompt = f"""[טקסט מקור (עם ניקוד) - החלק העיקרי]:
{content['source_content']}

[סקשן יעד מלא - יש לשכתב במדויק עם ניקוד בחלקים המודגשים בלבד]:
{content['target_content']}

הנחיות חשובות:
1. העתק את כל הסקשן הנ"ל במדויק, מילה במילה
2. הוסף ניקוד לכל טקסט שנמצא בין תגיות <b></b> (טקסט מודגש)
3. ודא שכל מילה מודגשת מקבלת את כל הניקוד הנדרש
4. השאר את כל שאר הטקסט בדיוק כפי שהוא, ללא שום ניקוד
5. שמור על כל תגיות ה-HTML במקומן המדויק
6. אל תוסיף תגיות <br> או כל תגית HTML אחרת
7. טקסט שאינו מודגש חייב להישאר ללא ניקוד, אפילו אם הוא זהה לטקסט במקור
8. החזר את הסקשן המלא בדיוק כפי שהוא, עם ניקוד רק בחלקים המודגשים"""

        # Log full prompt with clear separators
        self.logger.info("\n" + "="*50 + "\nFULL GEMINI PROMPT:\n" + "="*50 + "\n" + prompt)
        
        # Save to report file if provided
        if report_path:
            with open(report_path, 'a', encoding='utf-8') as report_file:
                report_file.write("\n" + "="*50 + "\n")
                report_file.write(f"GEMINI PROMPT FOR SECTION {content['target_header']}:\n")
                report_file.write("="*50 + "\n")
                # Save only a summary of the prompt to avoid extremely large files
                report_file.write(f"[Source content length: {len(content['source_content'])} chars]\n")
                report_file.write(f"[Target content length: {len(content['target_content'])} chars]\n")
                report_file.write("="*50 + "\n")
        
        st_log.log("שולח בקשה ל-Gemini...", "🔄")
        response = self.chat_session.send_message(prompt)
        
        # Log full response with clear separators
        self.logger.info("\n" + "="*50 + "\nFULL GEMINI RESPONSE:\n" + "="*50 + "\n" + response.text)
        
        # Save to report file if provided
        if report_path:
            with open(report_path, 'a', encoding='utf-8') as report_file:
                report_file.write("\n" + "="*50 + "\n")
                report_file.write(f"GEMINI RESPONSE:\n")
                report_file.write("="*50 + "\n")
                # Save only the first 500 characters of the response
                preview = response.text[:500] + "..." if len(response.text) > 500 else response.text
                report_file.write(f"{preview}\n")
                report_file.write("="*50 + "\n\n")
        
        st_log.log(f"התקבלה תשובה מ-Gemini", "✨")
        
        return response.text 