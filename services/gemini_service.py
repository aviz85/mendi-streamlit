import os
import google.generativeai as genai
from typing import Dict
import logging
import sys
import re  # Added for regex support
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
- העתק את כל הסקשן במדויק, מילה במילה, כולל כל ירידות השורה
- כל טקסט מודגש (בין תגיות <b></b>) חייב לקבל ניקוד מלא
- חשוב מאוד למצוא את הניקוד המתאים לכל מילה מודגשת, אפילו אם מילה דומה מופיעה בצורה שונה במקור
- שמור על כל ירידות השורה במקומן המדויק
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
        
        # Check if target content is too large (more than 100,000 chars)
        target_content = content['target_content']
        if len(target_content) > 100000:
            st_log.log(f"⚠️ תוכן היעד גדול מדי ({len(target_content)} תווים), מפצל לחלקים קטנים", "⚠️")
            return self._process_large_content(content, report_path)
        
        prompt = f"""[טקסט מקור (עם ניקוד) - החלק העיקרי]:
{content['source_content']}

[סקשן יעד מלא - יש לשכתב במדויק עם ניקוד בחלקים המודגשים בלבד]:
{content['target_content']}

הנחיות חשובות:
1. העתק את כל הסקשן הנ"ל במדויק, מילה במילה, כולל כל ירידות השורה
2. הוסף ניקוד מלא לכל טקסט שנמצא בין תגיות <b></b> (טקסט מודגש)
3. ודא שכל מילה מודגשת מקבלת את כל הניקוד הנדרש
4. השאר את כל שאר הטקסט בדיוק כפי שהוא, ללא שום ניקוד
5. שמור על כל תגיות ה-HTML במקומן המדויק
6. שמור על כל ירידות השורה במקומן המדויק - זה קריטי
7. אל תוסיף תגיות <br> או כל תגית HTML אחרת
8. אל תשנה את סדר המילים או התוכן
9. טקסט שאינו מודגש חייב להישאר ללא ניקוד, אפילו אם הוא זהה לטקסט מנוקד במקור
10. חפש בטקסט המקור את המילים הדומות ביותר למילים המודגשות כדי להוסיף להן ניקוד מתאים"""

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
        
    def _process_large_content(self, content: Dict, report_path: str = None) -> str:
        """Process large content by splitting it into chunks and processing each chunk"""
        source_content = content['source_content']
        target_content = content['target_content']
        target_header = content['target_header']
        
        # Find all <b> tags positions to split intelligently
        bold_positions = []
        for match in re.finditer(r'<b>.*?</b>', target_content, re.DOTALL):
            bold_positions.append((match.start(), match.end()))
        
        if not bold_positions:
            st_log.log("לא נמצאו תגי <b> בתוכן היעד", "⚠️")
            return target_content  # Return unchanged if no bold tags
            
        # Determine chunk size (aim for ~25 bold tags per chunk)
        total_bold_tags = len(bold_positions)
        chunk_count = max(1, total_bold_tags // 25)
        bold_tags_per_chunk = max(1, total_bold_tags // chunk_count)
        
        st_log.log(f"מפצל לכ-{chunk_count} חלקים עם ~{bold_tags_per_chunk} תגי <b> בכל חלק", "🔄")
        
        # Split content into chunks
        chunks = []
        current_chunk_start = 0
        
        for i in range(0, total_bold_tags, bold_tags_per_chunk):
            # If this is the last chunk, include everything to the end
            if i + bold_tags_per_chunk >= total_bold_tags:
                chunk_end = len(target_content)
            else:
                # Otherwise, end the chunk after the last bold tag in this group
                chunk_end = bold_positions[i + bold_tags_per_chunk - 1][1]
            
            # Extract chunk
            chunk = target_content[current_chunk_start:chunk_end]
            chunks.append(chunk)
            current_chunk_start = chunk_end
        
        # Process each chunk
        processed_chunks = []
        
        for idx, chunk in enumerate(chunks):
            st_log.log(f"מעבד חלק {idx+1} מתוך {len(chunks)}", "🔄")
            
            # Create a fresh chat session for each chunk
            new_session = self.model.start_chat()
            
            # Create chunk content dictionary
            chunk_content = {
                'source_content': source_content,
                'target_content': chunk,
                'target_header': f"{target_header} (חלק {idx+1}/{len(chunks)})"
            }
            
            # Construct prompt for this chunk
            prompt = f"""[טקסט מקור (עם ניקוד) - החלק העיקרי]:
{chunk_content['source_content']}

[חלק {idx+1} מתוך {len(chunks)} של סקשן יעד - יש לשכתב במדויק עם ניקוד בחלקים המודגשים בלבד]:
{chunk_content['target_content']}

הנחיות חשובות:
1. העתק את החלק הנ"ל במדויק, מילה במילה, כולל כל ירידות השורה
2. הוסף ניקוד מלא לכל טקסט שנמצא בין תגיות <b></b> (טקסט מודגש)
3. ודא שכל מילה מודגשת מקבלת את כל הניקוד הנדרש
4. השאר את כל שאר הטקסט בדיוק כפי שהוא, ללא שום ניקוד
5. שמור על כל תגיות ה-HTML במקומן המדויק
6. שמור על כל ירידות השורה במקומן המדויק - זה קריטי
7. אל תוסיף תגיות <br> או כל תגית HTML אחרת
8. אל תשנה את סדר המילים או התוכן
9. טקסט שאינו מודגש חייב להישאר ללא ניקוד, אפילו אם הוא זהה לטקסט מנוקד במקור
10. חפש בטקסט המקור את המילים הדומות ביותר למילים המודגשות כדי להוסיף להן ניקוד מתאים"""
            
            # Log chunk info
            if report_path:
                with open(report_path, 'a', encoding='utf-8') as report_file:
                    report_file.write("\n" + "="*50 + "\n")
                    report_file.write(f"CHUNK {idx+1}/{len(chunks)} FOR SECTION {target_header}:\n")
                    report_file.write("="*50 + "\n")
                    report_file.write(f"[Chunk length: {len(chunk)} chars]\n")
                    report_file.write("="*50 + "\n")
            
            # Send chunk to Gemini
            response = new_session.send_message(prompt)
            processed_chunks.append(response.text)
            
        # Combine processed chunks
        st_log.log(f"משלב {len(processed_chunks)} חלקים מעובדים", "🔄")
        combined_content = ''.join(processed_chunks)
        
        return combined_content 