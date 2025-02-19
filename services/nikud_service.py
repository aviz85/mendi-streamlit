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
        
        for para in doc.paragraphs:
            for run in para.runs:
                if run.bold:
                    text += f"**{run.text}**"
                else:
                    text += run.text
            text += "\n"
            
        return text, doc
    
    def _write_docx(self, content: str, template_doc: Document, output_path: str):
        """Write content back to DOCX preserving bold formatting"""
        doc = Document()
        
        # Copy styles from template
        doc.styles = template_doc.styles
        
        # Process content and write to doc
        paragraphs = content.split('\n')
        for para_text in paragraphs:
            if not para_text.strip():
                continue
                
            para = doc.add_paragraph()
            
            # Split by bold markers
            parts = re.split(r'(\*\*.*?\*\*)', para_text)
            
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    # Bold text
                    run = para.add_run(part[2:-2])
                    run.bold = True
                else:
                    # Regular text
                    para.add_run(part)
        
        doc.save(output_path)
        self.logger.info(f"💾 המסמך נשמר ב: {output_path}")

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