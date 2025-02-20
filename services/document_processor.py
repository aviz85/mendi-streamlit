import re
from typing import List, Dict, Tuple, Optional
import logging
from .usage_logger import streamlit_logger as st_log

class Section:
    def __init__(self, header: str, content: str):
        self.header = header
        self.content = content
        self.main_content: Optional[str] = None
        self.first_sentence: Optional[str] = None
        self._extract_main_content()
        
    def _extract_main_content(self):
        """Extract main content - first substantial paragraph until double newline"""
        # Look for first paragraph of 100+ chars and continue until double newline
        current_para = []
        found_main = False
        main_content = []
        
        for line in self.content.split('\n'):
            if not line.strip() and found_main:
                if not current_para:  # Second empty line in a row
                    break
                main_content.extend(current_para)
                main_content.append('')  # Add the newline
                current_para = []
            else:
                current_para.append(line)
                if not found_main and len(''.join(current_para).strip()) >= 100:
                    found_main = True
                    
        if current_para:  # Add any remaining content
            main_content.extend(current_para)
            
        if main_content:
            self.main_content = '\n'.join(main_content)
            # Extract first sentence
            sentences = re.split('[.!?]', main_content[0])
            if sentences:
                self.first_sentence = sentences[0].strip()

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
        
        st_log.log("מפצל את המסמך לחלקים...", "��")
        
        # Split while preserving all newlines
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if self._is_hebrew_letter_line(line):
                # Save previous section if exists
                if current_content:
                    # Join with original newlines
                    content = ""
                    for j, content_line in enumerate(current_content):
                        content += content_line
                        # Add original number of newlines after each line
                        if j < len(current_content) - 1:
                            next_non_empty = next((l for l in lines[i:] if l.strip()), None)
                            newlines = 1
                            if not next_non_empty:
                                newlines = 2
                            content += '\n' * newlines
                    sections.append(Section(current_header, content))
                    st_log.log(f"נמצא חלק: {line}", "📎")
                current_header = line
                current_content = []
            else:
                current_content.append(line)
                
        # Add last section
        if current_content:
            content = ""
            for j, line in enumerate(current_content):
                content += line
                if j < len(current_content) - 1:
                    content += '\n'
            sections.append(Section(current_header, content))
            
        st_log.log(f"נמצאו {len(sections)} חלקים", "✅")
        return sections

    def normalize_text(self, text: str) -> str:
        """Normalize text by removing nikud and optionally removing אהוי"""
        # Remove nikud
        text = re.sub(r'[\u05B0-\u05BC\u05C1-\u05C2\u05C4-\u05C5\u05C7]', '', text)
        # Keep spaces
        return text

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using character ratio"""
        longer = max(len(text1), len(text2))
        shorter = min(len(text1), len(text2))
        return shorter / longer if longer > 0 else 0

    def find_matching_sections(self, source_sections: List[Section], 
                             target_sections: List[Section],
                             similarity_threshold: float = 0.9) -> List[Tuple[Section, Section]]:
        """Find matching sections between source and target"""
        matches = []
        
        st_log.log("מחפש התאמות בין חלקי המסמכים...", "🔍")
        
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
                
                score = self._calculate_similarity(source_normalized, target_normalized)
                
                if score > best_score and score >= similarity_threshold:
                    best_score = score
                    best_match = target_section
            
            if best_match:
                matches.append((source_section, best_match))
                st_log.log(f"נמצאה התאמה: {source_section.header} ↔️ {best_match.header} ({best_score:.0%})", "✨")
        
        st_log.log(f"נמצאו {len(matches)} התאמות", "✅")
        return matches

    def _count_bold_parts(self, text: str) -> int:
        """Count number of bold parts in text (marked with <b></b>)"""
        return len(re.findall(r'<b>.*?</b>', text))

    def prepare_for_nikud(self, source_section: Section, target_section: Section) -> Dict:
        """Prepare content for sending to Gemini for nikud"""
        bold_count = self._count_bold_parts(target_section.content)
        st_log.log(f"מזהה חלקים מודגשים בחלק {target_section.header}... זוהו {bold_count} חלקים", "��")
        
        # Debug logs
        st_log.log("=== תוכן מקור ===", "📄")
        st_log.log(source_section.main_content[:200] + "...", "📝")
        st_log.log("=== תוכן יעד ===", "📄")
        st_log.log(target_section.content[:200] + "...", "📝")
        
        return {
            "source_content": source_section.main_content,
            "target_content": target_section.content,
            "source_header": source_section.header,
            "target_header": target_section.header
        } 