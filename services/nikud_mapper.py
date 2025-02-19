import re
from typing import Dict, List, Optional, Tuple
from docx import Document
from docx.shared import RGBColor
from rapidfuzz import fuzz
import logging
from difflib import SequenceMatcher, Match

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class NikudMapper:
    def __init__(self, bold_only: bool = False):
        self.bold_only = bold_only
        self.nikud_patterns = {
            'nikud': r'[\u05B0-\u05BC\u05C1-\u05C2\u05C4-\u05C5\u05C7]',
            'hebrew': r'[\u0590-\u05FF]'
        }
        
    def _create_virtual_copy(self, text: str) -> Tuple[List[str], List[str]]:
        """
        יצירת עותק וירטואלי של המילים המנוקדות
        
        Returns:
            Tuple[List[str], List[str]]: (מילים מנוקדות, מילים ללא ניקוד)
        """
        nikud_words = []  # מילים מנוקדות
        clean_words = []  # מילים ללא ניקוד
        
        for word in re.finditer(f"{self.nikud_patterns['hebrew']}+", text):
            if self._has_nikud(word.group()):
                nikud_words.append(word.group())
                clean_words.append(self._strip_nikud(word.group()))
        
        return nikud_words, clean_words

    def _find_overlap(self, source_words: List[str], target_text: str) -> Tuple[int, int, int, int]:
        """מציאת חפיפה בין הטקסטים"""
        target_words = re.findall(f"{self.nikud_patterns['hebrew']}+", target_text)
        
        if not target_words:
            return 0, 0, 0, 0
        
        # מציאת כל החפיפות האפשריות
        best_match = None
        best_score = 0
        min_size = 20  # מינימום מילים לחפיפה
        window_step = 10  # קפיצות של 10 מילים
        similarity_threshold = 85  # סף דמיון מופחת
        
        # חיפוש חפיפות בחלונות
        max_size = min(300, len(target_words))  # הגבלת גודל חלון
        
        for size in range(min_size, max_size + 1, window_step):
            for j in range(0, len(target_words) - size + 1, window_step):
                target_slice = ' '.join(target_words[j:j+size])
                
                # חיפוש בטקסט המקור
                for i in range(0, len(source_words) - size + 1, window_step):
                    source_slice = ' '.join(source_words[i:i+size])
                    
                    # חישוב דמיון
                    ratio = fuzz.ratio(source_slice, target_slice)
                    if ratio < similarity_threshold:
                        continue
                    
                    # חישוב ציון
                    position_score = 1 - (j / len(target_words))  # העדפה להתחלה
                    size_score = size / max_size  # העדפה לחפיפות ארוכות
                    ratio_score = ratio / 100  # דמיון טקסטואלי
                    
                    score = (
                        size_score * 0.5 +     # 50% משקל לאורך
                        ratio_score * 0.4 +    # 40% משקל לדמיון
                        position_score * 0.1    # 10% משקל למיקום
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_match = (i, i+size, j, j+size)
                        
                        # מפסיקים אם מצאנו חפיפה מספיק טובה
                        if score > 0.85:
                            return best_match
        
        return best_match or (0, 0, 0, 0)

    def _calc_context_score(self, source_words: List[str], target_words: List[str], match: Match) -> float:
        """חישוב ציון הקשר לחפיפה"""
        # בדיקת מילים לפני ואחרי החפיפה
        context_size = 2  # כמה מילים לבדוק בכל צד
        
        before_source = source_words[max(0, match.a-context_size):match.a]
        after_source = source_words[match.a+match.size:match.a+match.size+context_size]
        
        before_target = target_words[max(0, match.b-context_size):match.b]
        after_target = target_words[match.b+match.size:match.b+match.size+context_size]
        
        # חישוב דמיון בין ההקשרים
        before_ratio = fuzz.ratio(' '.join(before_source), ' '.join(before_target)) / 100
        after_ratio = fuzz.ratio(' '.join(after_source), ' '.join(after_target)) / 100
        
        return (before_ratio + after_ratio) / 2

    def _align_cursors(self, source_words: List[str], target_words: List[str], 
                      start_source: int, start_target: int) -> Tuple[int, int]:
        """יישור סמנים לתחילת החפיפה"""
        source_cursor = start_source
        target_cursor = start_target
        
        source_word = source_words[source_cursor]
        target_word = target_words[target_cursor]
        
        logger.info(
            f"מיקום סמן מקור: {source_cursor} מו��ה על המילה - {source_word}\n"
            f"מיקום סמן יעד: {target_cursor} מורה על המילה - {target_word}"
        )
        
        return source_cursor, target_cursor

    def add_nikud_to_text(self, source_text: str, target_text: str) -> str:
        """הוספת ניקוד לטקסט"""
        # יצירת עותק וירטואלי
        source_nikud, source_clean = self._create_virtual_copy(source_text)
        target_words = re.findall(f"{self.nikud_patterns['hebrew']}+", target_text)
        
        # מציאת חפיפה
        start_s, end_s, start_t, end_t = self._find_overlap(source_clean, target_text)
        
        # אם לא נמצאה חפיפה, מחזירים את הטקסט המקורי
        if start_s == end_s == start_t == end_t == 0:
            return target_text
        
        # עיבוד הטקסט לפי החפיפה שנמצאה
        result = []
        
        # מילים לפני החפיפה
        result.extend(target_words[:start_t])
        
        # מילים בתוצאה החפיפה
        for i in range(start_t, end_t):
            source_idx = start_s + (i - start_t)
            result.append(source_nikud[source_idx])
        
        # מילים אחרי החפיפה
        result.extend(target_words[end_t:])
        
        return ' '.join(result)

    def _has_nikud(self, text: str) -> bool:
        return bool(re.search(self.nikud_patterns['nikud'], text))

    def _has_hebrew(self, text: str) -> bool:
        return bool(re.search(self.nikud_patterns['hebrew'], text))

    def _strip_nikud(self, text: str) -> str:
        return re.sub(self.nikud_patterns['nikud'], '', text)

    def _is_bold(self, word: str) -> bool:
        # TODO: לממש בדיקת הדגשה לפי המסמך
        return True

    def process_docx(self, input_path: str, output_path: str, source_path: str = None) -> None:
        """
        עיבוד קובץ Word והוספת ניקוד
        
        Args:
            input_path: נתיב לקובץ הקלט
            output_path: נתיב לקובץ הפלט
            source_path: נתיב לקובץ המקור המנוקד. אם לא צוין, משתמש בקובץ הקלט
        """
        logger.info(f"מעבד קבצים:\nמקור: {source_path or input_path}\nלט: {input_path}")
        
        # קריאת קובץ המקור והכנת המילים המנוקדות
        source_doc = Document(source_path or input_path)
        source_text = '\n'.join(p.text for p in source_doc.paragraphs)
        source_nikud, source_clean = self._create_virtual_copy(source_text)
        
        # קריאת קובץ היעד
        target_doc = Document(input_path)
        
        # עיבוד כל פסקה
        for paragraph in target_doc.paragraphs:
            # מציאת חפיפה לכל הפסקה
            paragraph_text = paragraph.text
            if not self._has_hebrew(paragraph_text):
                continue
            
            start_s, end_s, start_t, end_t = self._find_overlap(source_clean, paragraph_text)
            
            # עיבוד הריצות בפסקה
            for run in paragraph.runs:
                if run.bold or not self.bold_only:
                    original_text = run.text
                    if self._has_hebrew(original_text):
                        run.text = self.add_nikud_to_text(source_text, original_text)
        
        # שמירת הקובץ
        target_doc.save(output_path)
        logger.info(f"הקובץ נשמר: {output_path}")

    def test_known_dataset(self) -> None:
        """בדיקת המנקד על דאטה סט ידוע"""
        # דוגמה מוכרת עם ניקוד - עם שוליים נוספים
        source_text = """
        וַיְהִי בִּימֵי אֲחַשְׁוֵרוֹשׁ הוּא אֲחַשְׁוֵרוֹשׁ הַמֹּלֵךְ מֵהֹדּוּ וְעַד כּוּשׁ. בַּיָּמִים הָה��ם כְּשֶׁבֶת הַמֶּלֶךְ אֲחַשְׁוֵרוֹשׁ עַל כִּסֵּא מַלְכוּתוֹ.
        בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ. וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת עַל פְּנֵי הַמָּיִם.
        וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי אוֹר. וַיַּרְא אֱלֹהִים אֶת הָאוֹר כִּי טוֹב וַיַּבְדֵּל אֱלֹהִים בֵּין הָאוֹר וּבֵין הַחֹשֶׁךְ.
        הַתְּפִלָּה הִיא עֲבוֹדַת הַלֵּב, וְהִיא עִקַּר הָעֲבוֹדָה שֶׁבַּלֵּב. בִּזְמַן שֶׁבֵּית הַמִּקְדָּשׁ הָיָה קַיָּם, הָיְתָה הָעֲבוֹדָה בְּקָרְבָּנוֹת.
        וְעַכְשָׁיו שֶׁאֵין לָנוּ לֹא כֹהֵן וְלֹא מִזְבֵּחַ, אֵין לָנוּ אֶלָּא תְּפִלָּה. וּתְפִלָּה זוֹ צְרִיכָה לִהְיוֹת בְּכַוָּנָה וּבְרָצוֹן.
        וְכָךְ אָמְרוּ חֲכָמִים: תְּפִלָּה בְּלֹא כַוָּנָה כְּגוּף בְּלֹא נְשָׁמָה. וְעוֹד אָמְרוּ: הַמִּתְפַּלֵּל צָרִיךְ שֶׁיְּכַוֵּן אֶת לִבּוֹ לַשָּׁמַיִם.
        """
        
        # טקסט יעד עם חלקים חופפים וחלקים שונים
        target_text = """
        בראשית ברא אלוהים את השמים ואת הארץ. והארץ היתה תוהו ובוהו וחושך על פני תהום ורוח אלוהים מרחפת על פני המים.
        ויאמר אלוהים יהי אור ויהי אור. וירא אלוהים את האור כי טוב ויבדל אלוהים בין האור ובין החושך.
        התפילה היא עבודת הלב, והיא עיקר העבודה שבלב. בזמן שבית המקדש היה קיים, היתה העבודה בקרבנות.
        ועכשיו שאין לנו לא כהן ולא מזבח, אין לנו אלא תפילה. ותפילה זו צריכה להיות בכוונה וברצון.
        וכך אמרו חכמים: תפילה בלא כוונה כגוף בלא נשמה. ועוד אמרו: המתפלל צריך שיכוון את לבו לשמים.
        """
        
        logger.info("\n=== בדיקת דאטה סט ידוע ===")
        
        # יצירת עותק וירטואלי
        source_nikud, source_clean = self._create_virtual_copy(source_text)
        
        # מציאת חפיפה
        start_s, end_s, start_t, end_t = self._find_overlap(source_clean, target_text)
        
        # בדיקת תוצאות
        if start_s == end_s == start_t == end_t == 0:
            logger.error("❌ נכשל: לא נמצאה חפיפה בדאטה סט ידוע")
            return
        
        result = self.add_nikud_to_text(source_text, target_text)
        
        # בדיקה שהתוצאה מכילה ניקוד
        if not self._has_nikud(result):
            logger.error("❌ נכשל: התוצאה לא מכילה ניקוד")
            return
        
        logger.info("✓ הצליח: נמצאה חפיפה והתוצאה מכילה ניקוד")
        logger.info(f"תוצאה:\n{result}")