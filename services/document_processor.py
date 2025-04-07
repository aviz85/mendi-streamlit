"""
DocumentProcessor - Class for processing and converting documents

This class serves as a coordinator for the document processing workflow, including:
1. Reading DOCX documents
2. Analyzing sections and headers
3. Processing and converting content to different formats
4. Writing the processed document to a file

The class orchestrates all stages of the process in an organized and coordinated manner.
"""

import logging
import os
from typing import List, Dict, Any, Tuple, Optional, Union
import tempfile

from docx import Document

from .docx_reader import DocxReader
from .docx_writer import DocxWriter
from .section_analyzer import SectionAnalyzer
from .text_patterns import SectionType
from .usage_logger import streamlit_logger as st_log

class DocumentProcessor:
    """Class for processing and converting documents"""
    
    def __init__(self):
        """Initialize a new document processor"""
        self.logger = logging.getLogger(__name__)
        self.docx_reader = DocxReader()
        self.docx_writer = DocxWriter()
        self.section_analyzer = SectionAnalyzer()
        
    def process_document(self, input_file_path: str, output_file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a DOCX document and return its processed structure
        
        Parameters:
            input_file_path: Path to the input file
            output_file_path: Path to save the processed file (optional)
            
        Returns:
            Dictionary containing the processed structure of the document and additional information
        """
        st_log.log(f"מתחיל עיבוד מסמך: {os.path.basename(input_file_path)}", "📄")
        
        # Read DOCX file
        paragraphs, doc = self.docx_reader.read_docx_raw(input_file_path)
        
        if not paragraphs:
            st_log.log("לא נמצאו פסקאות במסמך", "⚠️")
            return {"error": "לא נמצאו פסקאות במסמך"}
            
        # Analyze sections
        sections = self.section_analyzer.split_to_sections(paragraphs)
        
        # Get base statistics
        stats = {
            "paragraphs_count": len(paragraphs),
            "sections_count": self._count_sections(sections),
            "bold_segments": self._count_bold_segments(input_file_path)
        }
        
        # Process the output file if needed
        if output_file_path:
            self._save_processed_document(sections, doc, output_file_path)
            
        # Return the processed structure
        result = {
            "sections": sections,
            "stats": stats,
            "output_file": output_file_path
        }
        
        st_log.log(f"עיבוד המסמך הושלם: {stats['paragraphs_count']} פסקאות, {stats['sections_count']} סעיפים", "✅")
        return result
        
    def _count_sections(self, sections: List[Dict[str, Any]]) -> int:
        """
        Count the number of sections (including subsections) in the section structure
        
        Parameters:
            sections: Section structure created by SectionAnalyzer
            
        Returns:
            Total number of sections
        """
        count = 0
        
        def count_recursive(section_list):
            nonlocal count
            for section in section_list:
                # Count this section
                count += 1
                # Count children recursively
                if "children" in section and section["children"]:
                    count_recursive(section["children"])
                    
        count_recursive(sections)
        return count
        
    def _count_bold_segments(self, file_path: str) -> int:
        """
        Count the number of bold segments in the document
        
        Parameters:
            file_path: Path to the document file
            
        Returns:
            Number of bold segments
        """
        # Use DocxReader to get bold segments count
        html_content, bold_count = self.docx_reader.read_docx_html(file_path)
        return bold_count
        
    def _save_processed_document(self, sections: List[Dict[str, Any]], 
                               original_doc: Document, output_path: str):
        """
        Save the processed document to a DOCX file
        
        Parameters:
            sections: Processed section structure
            original_doc: Original Document object (for preserving styles)
            output_path: Path to save the file
        """
        # Convert sections to HTML format (with bold tags)
        content = self._sections_to_html(sections)
        
        # Write to output file
        try:
            self.docx_writer.write_docx(content, original_doc, output_path)
            st_log.log(f"המסמך המעובד נשמר בהצלחה: {os.path.basename(output_path)}", "💾")
        except Exception as e:
            st_log.log(f"שגיאה בשמירת המסמך: {str(e)}", "❌")
            raise
            
    def _sections_to_html(self, sections: List[Dict[str, Any]]) -> str:
        """
        Convert the section structure to HTML format with support for <b> tags
        
        Parameters:
            sections: Section structure
            
        Returns:
            HTML string representing the entire document
        """
        result = []
        
        def process_section(section, level=0):
            # Add title (with appropriate formatting)
            if section["title"]:
                # Make titles bold
                if level == 0:  # Main title
                    result.append(f"<b>{section['title']}</b>")
                else:
                    result.append(f"<b>{section['title']}</b> {section['text']}")
            # Add text (if not already added with title)
            elif section["text"]:
                result.append(section["text"])
                
            # Process children with increased level
            if "children" in section and section["children"]:
                for child in section["children"]:
                    process_section(child, level + 1)
                    
        # Process all sections
        for section in sections:
            process_section(section)
            
        # Join with newlines
        return "\n".join(result)
        
    def create_preview(self, sections: List[Dict[str, Any]]) -> str:
        """
        Create a preview of the processed document in HTML format
        
        Parameters:
            sections: Section structure
            
        Returns:
            HTML string for display
        """
        result = ["<div class='document-preview'>"]
        
        def process_section(section, level=0):
            # Add title with appropriate heading
            if section["title"]:
                heading_level = min(level + 1, 6)  # h1 to h6
                
                if level == 0:  # Main title
                    result.append(f"<h{heading_level} class='doc-title'>{section['title']}</h{heading_level}>")
                else:
                    # Add section title with appropriate class based on section type
                    section_class = section["type"].name.lower() if "type" in section else "other"
                    result.append(f"<div class='section-header section-{section_class}'>")
                    result.append(f"<h{heading_level}>{section['title']}</h{heading_level}>")
                    result.append("</div>")
                    
                    # Add section text
                    if section["text"]:
                        result.append(f"<div class='section-content'>{section['text']}</div>")
            # Add text (if not already added with title)
            elif section["text"]:
                result.append(f"<div class='section-content'>{section['text']}</div>")
                
            # Process children with increased level
            if "children" in section and section["children"]:
                result.append("<div class='section-children'>")
                for child in section["children"]:
                    process_section(child, level + 1)
                result.append("</div>")
                    
        # Process all sections
        for section in sections:
            process_section(section)
            
        result.append("</div>")
        
        # Join with newlines
        return "\n".join(result)
