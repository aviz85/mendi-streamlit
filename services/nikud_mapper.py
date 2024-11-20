import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple
from docx import Document
from docx.shared import RGBColor
from docx.text.run import Run

class HebrewTextProcessor:
    def __init__(self, source_nikud_docx_path: str):
        """קורא את הטקסט המנוקד מקובץ DOCX"""
        self.full_source = self.read_source_docx(source_nikud_docx_path)
        self.source_nikud = self.extract_nikud_section()
        self.nikud_map = self.build_word_mapping()
        
    def read_source_docx(self, docx_path: str) -> str:
        """קריאת כל הטקסט מקובץ DOCX"""
        doc = Document(docx_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)

    def has_nikud(self, text: str) -> bool:
        """בדיקה אם יש ניקוד בטקסט"""
        nikud_pattern = re.compile(r'[\u05B0-\u05BC\u05C1-\u05C2\u05C4-\u05C5\u05C7]')
        return bool(nikud_pattern.search(text))

    def extract_nikud_section(self) -> str:
        """מציאת החלק המנוקד בטקסט"""
        # פיצול לפי מילים תוך שמירה על סימני פיסוק ורווחים
        parts = re.split(r'([\u0590-\u05FF]+|\s+|[^\u0590-\u05FF\s]+)', self.full_source)
        
        start_idx = None
        end_idx = None
        
        # מציאת המילה הראשונה עם ניקוד
        for i, part in enumerate(parts):
            if self.has_hebrew(part) and self.has_nikud(part):
                start_idx = i
                break
        
        # מציאת המילה האחרונה עם ניקוד
        for i in range(len(parts) - 1, -1, -1):
            if self.has_hebrew(parts[i]) and self.has_nikud(parts[i]):
                end_idx = i + 1
                break
        
        if start_idx is not None and end_idx is not None:
            nikud_text = ''.join(parts[start_idx:end_idx])
            print(f"נמצא טקסט מנוקד באורך {len(nikud_text)} תווים")
            print(f"מתחיל במילה: {parts[start_idx]}")
            print(f"מסתיים במילה: {parts[end_idx-1]}")
            return nikud_text
        else:
            raise ValueError("לא נמצא טקסט מנוקד במסמך המקור")
        
    def strip_nikud(self, text: str) -> str:
        """הסרת ניקוד מטקסט עברי"""
        nikud_chars = (
            '\u05B0-\u05BC'  # ניקוד עברי בסיסי
            '\u05C1-\u05C2'  # שין ושׂין
            '\u05C4-\u05C5'  # טעמים
            '\u05C7'         # קמץ קטן
        )
        return re.sub(f'[{nikud_chars}]', '', text)

    def has_hebrew(self, text: str) -> bool:
        """בדיקה אם יש תווים בעברית בטקסט"""
        hebrew_chars = re.compile(r'[\u0590-\u05FF]')
        return bool(hebrew_chars.search(text))

    def build_word_mapping(self) -> Dict[str, str]:
        """בניית מיפוי בין מילים לא מנוקדות למילים מנוקדות"""
        # פיצול לפי מילים תוך שמירה על סימני פיסוק
        parts = re.split(r'([\u0590-\u05FF]+|\s+|[^\u0590-\u05FF\s]+)', self.source_nikud)
        word_map = {}
        
        for part in parts:
            if self.has_hebrew(part) and self.has_nikud(part):
                clean_word = self.strip_nikud(part)
                word_map[clean_word] = part
                
        print(f"נבנה מיפוי של {len(word_map)} מילים ייחודיות מנוקדות")
        return word_map

    def find_best_match(self, word: str) -> str:
        """מציאת ההתאמה הטובה ביותר למילה"""
        if not self.has_hebrew(word):
            return word
            
        clean_word = self.strip_nikud(word)
        
        # חיפוש התאמה מדויקת
        if clean_word in self.nikud_map:
            nikud_word = self.nikud_map[clean_word]
            print(f"נמצאה התאמה מדויקת: {word} -> {nikud_word}")
            return nikud_word
            
        # חיפוש התאמה קרובה
        best_ratio = 0
        best_match = word
        
        for clean_source, nikud_source in self.nikud_map.items():
            ratio = SequenceMatcher(None, clean_word, clean_source).ratio()
            if ratio > best_ratio and ratio >= 0.8:
                best_ratio = ratio
                best_match = nikud_source
                print(f"נמצאה התאמה חלקית: {word} -> {best_match} (דמיון: {best_ratio:.2%})")
                
        return best_match

def process_docx(source_nikud_docx: str, input_docx: str, output_docx: str) -> None:
    """עיבוד קובץ Word"""
    print("מתחיל עיבוד...")
    
    # יצירת מעבד הטקסט
    processor = HebrewTextProcessor(source_nikud_docx)
    
    # קריאת קובץ ה-Word שצריך לנקד
    doc = Document(input_docx)
    print("נקרא קובץ Word לניקוד")
    
    total_bold_runs = 0
    processed_runs = 0
    
    # מעבר על כל הפסקאות והרצות
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if run.bold:
                total_bold_runs += 1
                text = run.text
                
                if processor.has_hebrew(text):
                    processed_runs += 1
                    print(f"\nמעבד קטע מודגש: {text}")
                    
                    # פיצול לחלקים תוך שמירה על רווחים וסימני פיסוק
                    parts = re.split(r'([\u0590-\u05FF]+|\s+|[^\u0590-\u05FF\s]+)', text)
                    processed_parts = []
                    
                    for part in parts:
                        if processor.has_hebrew(part):
                            nikud_part = processor.find_best_match(part)
                            processed_parts.append(nikud_part)
                        else:
                            processed_parts.append(part)
                    
                    run.text = ''.join(processed_parts)
    
    print(f"\nסיכום:")
    print(f"נמצאו {total_bold_runs} קטעים מודגשים")
    print(f"עובדו {processed_runs} קטעים עם טקסט עברי")
    
    # שמירת הקובץ המעובד
    doc.save(output_docx)
    print(f"הקובץ המנוקד נשמר ב: {output_docx}")

if __name__ == "__main__":
    source_nikud_docx = "source_nikud.docx"    # קובץ Word עם הטקסט המנוקד
    input_docx = "input.docx"                  # קובץ Word שצריך לנקד
    output_docx = "output_nikud.docx"          # קובץ התוצאה
    
    process_docx(source_nikud_docx, input_docx, output_docx)