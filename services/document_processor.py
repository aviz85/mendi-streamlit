import re
from typing import List, Dict, Tuple, Optional
import logging

class Section:
    def __init__(self, header: str, content: str):
        self.header = header
        self.content = content
        self.main_content: Optional[str] = None
        self.first_sentence: Optional[str] = None
        self._extract_main_content()
        
    def _extract_main_content(self):
        """Extract main content - paragraph with 100+ chars and following until double newline"""
        paragraphs = self.content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if len(para.strip()) >= 100:
                # Found main paragraph, include it and following until double newline
                self.main_content = '\n'.join(paragraphs[i:])
                # Extract first sentence
                sentences = re.split('[.!?]', para)
                if sentences:
                    self.first_sentence = sentences[0].strip()
                break

class DocumentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def _is_hebrew_letter_line(self, line: str) -> bool:
        """Check if line contains only 1-3 Hebrew letters"""
        # Remove whitespace
        line = line.strip()
        # Check if contains only Hebrew letters
        hebrew_pattern = re.compile(r'^[\u0590-\u05FF]{1,3}$')
        return bool(hebrew_pattern.match(line))

    def split_to_sections(self, text: str) -> List[Section]:
        """Split document into sections based on Hebrew letter delimiters"""
        sections = []
        current_header = ""
        current_content = []
        
        self.logger.info("🔍 מתחיל לפצל את המסמך לחלקים")
        
        lines = text.split('\n')
        for line in lines:
            if self._is_hebrew_letter_line(line):
                # Save previous section if exists
                if current_content:
                    sections.append(Section(current_header, '\n'.join(current_content)))
                    self.logger.info(f"📑 נמצא חלק חדש המתחיל ב: {line}")
                current_header = line
                current_content = []
            else:
                current_content.append(line)
                
        # Add last section
        if current_content:
            sections.append(Section(current_header, '\n'.join(current_content)))
            
        self.logger.info(f"✅ הפיצול הושלם. נמצאו {len(sections)} חלקים")
        return sections

    def normalize_text(self, text: str) -> str:
        """Normalize text by removing nikud and optionally removing אהוי"""
        # Remove nikud
        text = re.sub(r'[\u05B0-\u05BC\u05C1-\u05C2\u05C4-\u05C5\u05C7]', '', text)
        # Keep spaces
        return text

    def find_matching_sections(self, source_sections: List[Section], 
                             target_sections: List[Section],
                             similarity_threshold: float = 0.9) -> List[Tuple[Section, Section]]:
        """Find matching sections between source and target based on first sentence similarity"""
        matches = []
        
        self.logger.info("🔄 מחפש התאמות בין חלקי המסמכים")
        
        for source_section in source_sections:
            if not source_section.first_sentence:
                continue
                
            source_normalized = self.normalize_text(source_section.first_sentence)
            
            best_match = None
            best_score = 0
            
            for target_section in target_sections:
                if not target_section.first_sentence:
                    continue
                    
                target_normalized = self.normalize_text(target_section.first_sentence)
                
                # Calculate similarity (implement your preferred method)
                # For now using simple character ratio
                longer = max(len(source_normalized), len(target_normalized))
                shorter = min(len(source_normalized), len(target_normalized))
                score = shorter / longer if longer > 0 else 0
                
                if score > best_score and score >= similarity_threshold:
                    best_score = score
                    best_match = target_section
            
            if best_match:
                matches.append((source_section, best_match))
                self.logger.info(f"✨ נמצאה התאמה: {source_section.header} ↔️ {best_match.header}")
        
        self.logger.info(f"✅ נמצאו {len(matches)} התאמות")
        return matches

    def prepare_for_nikud(self, source_section: Section, target_section: Section) -> Dict:
        """Prepare content for sending to Gemini for nikud"""
        return {
            "source_content": source_section.main_content,
            "target_content": target_section.content,
            "source_header": source_section.header,
            "target_header": target_section.header
        } 