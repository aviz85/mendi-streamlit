import logging
from pathlib import Path
from typing import Tuple, Dict
from docx import Document
import re

from .document_processor import DocumentProcessor
from .gemini_service import GeminiService
from .usage_logger import streamlit_logger as st_log

class NikudService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.doc_processor = DocumentProcessor()
        self.gemini = GeminiService()
        
    def _read_docx(self, file_path: str) -> Tuple[str, Document]:
        """Read DOCX file and extract text while preserving bold formatting"""
        doc = Document(file_path)
        text = ""
        bold_count = 0
        
        st_log.log(f"קורא קובץ: {file_path}", "📖")
        
        for para in doc.paragraphs:
            para_text = ""
            current_bold_text = ""
            last_was_bold = False
            
            for run in para.runs:
                if run.bold:
                    if not last_was_bold:  # Start of bold section
                        current_bold_text = run.text
                    else:  # Continue bold section
                        current_bold_text += run.text
                    last_was_bold = True
                else:
                    if last_was_bold:  # End of bold section
                        para_text += f"<b>{current_bold_text}</b>"
                        current_bold_text = ""
                        bold_count += 1
                    para_text += run.text
                    last_was_bold = False
            
            # Handle any remaining bold text at end of paragraph
            if last_was_bold and current_bold_text:
                para_text += f"<b>{current_bold_text}</b>"
                bold_count += 1
            
            text += para_text + "\n"
        
        st_log.log(f"זוהו {bold_count} קטעים מודגשים", "🔍")
        return text, doc
    
    def _write_docx(self, content: str, template_doc: Document, output_path: str):
        """Write content back to DOCX preserving all formatting"""
        doc = Document()
        
        # Copy styles from template
        doc.styles._element = template_doc.styles._element
        
        # Set RTL at document level using XML
        doc._body._element.set('bidi', '1')
        
        # Process content and write to doc
        paragraphs = content.split('\n')
        for para_text in paragraphs:
            if not para_text.strip():
                continue
                
            para = doc.add_paragraph()
            # Set RTL and right alignment
            para.paragraph_format.alignment = 2  # WD_ALIGN_PARAGRAPH.RIGHT
            para.style = template_doc.paragraphs[0].style if template_doc.paragraphs else None
            
            # Set paragraph direction
            pPr = para._p.get_or_add_pPr()
            pPr.set('bidi', '1')
            
            # Split by bold markers - using non-greedy match for nested tags
            parts = re.split(r'(<b>.*?</b>)', para_text)
            
            for part in parts:
                if part.startswith('<b>') and part.endswith('</b>'):
                    # Bold text - extract content between tags
                    text = re.search(r'<b>(.*?)</b>', part).group(1)
                    run = para.add_run(text)
                    run.bold = True
                    
                    # Set run direction
                    rPr = run._r.get_or_add_rPr()
                    rPr.set('rtl', '1')
                else:
                    # Regular text
                    if part.strip():
                        run = para.add_run(part)
                        # Set run direction
                        rPr = run._r.get_or_add_rPr()
                        rPr.set('rtl', '1')
        
        # Save with error handling
        try:
            doc.save(output_path)
            st_log.log(f"המסמך נשמר בהצלחה: {output_path}", "💾")
        except Exception as e:
            st_log.log(f"שגיאה בשמירת המסמך: {str(e)}", "❌")
            raise

    def process_files(self, source_path: str, target_path: str, output_path: str):
        """Process source and target files to add nikud"""
        st_log.log("מתחיל תהליך הוספת ניקוד", "🚀")
        
        # Read files
        st_log.log("קורא קבצים...", "📂")
        source_text, source_doc = self._read_docx(source_path)
        target_text, target_doc = self._read_docx(target_path)
        
        # Split to sections
        source_sections = self.doc_processor.split_to_sections(source_text)
        target_sections = self.doc_processor.split_to_sections(target_text)
        
        # Find matching sections
        matches = self.doc_processor.find_matching_sections(source_sections, target_sections)
        
        # Process each match with Gemini
        st_log.log("מעבד חלקים...", "⚙️")
        processed_sections = {}
        for source_section, target_section in matches:
            content = self.doc_processor.prepare_for_nikud(source_section, target_section)
            processed_content = self.gemini.add_nikud(content)
            processed_sections[target_section.header] = processed_content
            
        # Reconstruct document
        st_log.log("מרכיב מחדש את המסמך...", "🔄")
        final_content = []
        for section in target_sections:
            if section.header in processed_sections:
                final_content.append(processed_sections[section.header])
            else:
                final_content.append(section.content)
                
        # Write output
        self._write_docx('\n'.join(final_content), target_doc, output_path)
        st_log.log("המסמך נשמר בהצלחה", "💾")

    def add_nikud(self, text: str) -> str:
        """
        Add nikud to Hebrew text (currently returns dummy data)
        """
        words = text.split()
        result = []
        
        for word in words:
            result.append(self.dummy_mappings.get(word, word))
            
        return " ".join(result)

    def remove_nikud(self, text: str) -> str:
        """
        Remove nikud from Hebrew text
        """
        # Unicode ranges for nikud marks
        nikud_pattern = r'[\u05B0-\u05BC\u05C1-\u05C2\u05C4-\u05C5\u05C7]'
        import re
        return re.sub(nikud_pattern, '', text)

    def test(self) -> Dict[str, bool]:
        """
        Run basic tests with dummy data
        """
        test_cases = {
            "Basic word": {
                "input": "שלום",
                "expected": "שָׁלוֹם"
            },
            "Multiple words": {
                "input": "ברוך הבא",
                "expected": "בָּרוּךְ הַבָּא"
            }
        }
        
        results = {}
        for name, case in test_cases.items():
            result = self.add_nikud(case["input"])
            results[name] = result == case["expected"]
            
        return results 