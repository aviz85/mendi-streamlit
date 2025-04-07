"""
SectionAnalyzer - Class for identifying sections and headers in legal documents

This class provides functionality for identifying sections, headers, and hierarchical structure
in legal documents, allowing the content to be divided into sections and subsections.
"""

import logging
import re
from typing import List, Dict, Tuple, Any, Union

from .text_patterns import (is_hebrew_letter, get_next_letter, 
                          section_patterns, detect_section_type, 
                          is_section_header, SectionType)
from .usage_logger import streamlit_logger as st_log

class SectionAnalyzer:
    """Class for identifying and analyzing document sections"""
    
    def __init__(self):
        """Initialize a new section analyzer"""
        self.logger = logging.getLogger(__name__)
        
    def split_to_sections(self, paragraphs: List[str]) -> List[Dict[str, Any]]:
        """
        Divides a list of paragraphs into a hierarchical structure of sections
        
        Parameters:
            paragraphs: List of paragraphs from the document
            
        Returns:
            List of sections, where each section contains information like title, text, and subsections
        """
        st_log.log("מתחיל ניתוח מבנה הסעיפים במסמך", "🔍")
        
        if not paragraphs:
            st_log.log("אין פסקאות לניתוח", "⚠️")
            return []
            
        # Remove empty paragraphs
        paragraphs = [p for p in paragraphs if p and p.strip()]
        
        # Initialize result with main section (the entire document as one section)
        main_section = {
            "title": "",  # We'll try to find title later
            "text": "",
            "type": SectionType.MAIN,
            "children": []
        }
        
        # Scan for potential title in the first few paragraphs
        for i in range(min(3, len(paragraphs))):
            if not is_section_header(paragraphs[i]):
                # If there's no recognized section pattern, it might be a title
                main_section["title"] = paragraphs[i]
                # Remove the title from the list of paragraphs
                paragraphs = paragraphs[1:]
                break
                
        # Analyze sections recursively
        self._analyze_sections(paragraphs, main_section, top_level=True)
        
        st_log.log(f"ניתוח הסעיפים הסתיים: {len(main_section['children'])} סעיפים ראשיים זוהו", "✅")
        return [main_section]
        
    def _analyze_sections(self, paragraphs: List[str], parent_section: Dict[str, Any], 
                          current_index: int = 0, top_level: bool = False) -> int:
        """
        Analyzes the hierarchical structure of sections in a list of paragraphs recursively
        
        Parameters:
            paragraphs: List of paragraphs to analyze
            parent_section: The parent section to which subsections will be added
            current_index: The current index in the paragraphs list
            top_level: Whether this is a top-level analysis
            
        Returns:
            The new index after analyzing all sections
        """
        if current_index >= len(paragraphs):
            return current_index
            
        # Extract patterns we're looking for at the current level
        current_section_type = None
        section_text = ""
        
        # For top level, look for numbered sections (1., 2., etc.)
        if top_level:
            pattern_to_find = section_patterns[SectionType.NUMBERED]
        # When inside a numbered section, look for lettered sections (א., ב., etc.)
        elif parent_section["type"] == SectionType.NUMBERED:
            pattern_to_find = section_patterns[SectionType.HEBREW_LETTER]
        # When inside a lettered section, look for sub-lettered sections ((1), (2), etc.)
        elif parent_section["type"] == SectionType.HEBREW_LETTER:
            pattern_to_find = section_patterns[SectionType.PARENTHESIS_NUMBER]
        # Other cases - simply add text to parent
        else:
            # Add all remaining text to parent_section and return
            parent_section["text"] += "\n".join(paragraphs[current_index:])
            return len(paragraphs)
            
        i = current_index
        last_section = None
        
        while i < len(paragraphs):
            paragraph = paragraphs[i]
            
            # Detect section type for current paragraph
            section_type = detect_section_type(paragraph)
            
            # Check if this paragraph starts a new section at the current level
            if section_type == SectionType.NUMBERED and top_level:
                # Start of a new numbered top-level section
                match = re.match(pattern_to_find, paragraph)
                if match:
                    # If we were processing a section, finalize it
                    if current_section_type is not None and last_section is not None:
                        last_section["text"] = section_text.strip()
                    
                    # Extract the section number and content
                    section_number = match.group(1)
                    content = paragraph[match.end():].strip()
                    
                    # Create a new section
                    new_section = {
                        "title": f"{section_number}.",
                        "text": content,
                        "type": SectionType.NUMBERED,
                        "children": []
                    }
                    
                    # Add to parent
                    parent_section["children"].append(new_section)
                    
                    # Update tracking variables
                    current_section_type = SectionType.NUMBERED
                    section_text = content
                    last_section = new_section
                    
                    # Move to next paragraph
                    i += 1
                    continue
            
            # For Hebrew-lettered sections inside a numbered section
            elif section_type == SectionType.HEBREW_LETTER and parent_section["type"] == SectionType.NUMBERED:
                match = re.match(pattern_to_find, paragraph)
                if match:
                    # If we were processing a section, process its children recursively
                    if current_section_type is not None and last_section is not None:
                        last_section["text"] = section_text.strip()
                        i = self._analyze_sections(paragraphs, last_section, i)
                        continue
                    
                    # Extract the section letter and content
                    section_letter = match.group(1)
                    content = paragraph[match.end():].strip()
                    
                    # Create a new section
                    new_section = {
                        "title": f"{section_letter}.",
                        "text": content,
                        "type": SectionType.HEBREW_LETTER,
                        "children": []
                    }
                    
                    # Add to parent
                    parent_section["children"].append(new_section)
                    
                    # Update tracking variables
                    current_section_type = SectionType.HEBREW_LETTER
                    section_text = content
                    last_section = new_section
                    
                    # Move to next paragraph
                    i += 1
                    continue
            
            # For parenthesis-numbered sections inside a Hebrew-lettered section
            elif section_type == SectionType.PARENTHESIS_NUMBER and parent_section["type"] == SectionType.HEBREW_LETTER:
                match = re.match(pattern_to_find, paragraph)
                if match:
                    # If we were processing a section, process its children recursively
                    if current_section_type is not None and last_section is not None:
                        last_section["text"] = section_text.strip()
                        i = self._analyze_sections(paragraphs, last_section, i)
                        continue
                    
                    # Extract the section number and content
                    section_number = match.group(1)
                    content = paragraph[match.end():].strip()
                    
                    # Create a new section
                    new_section = {
                        "title": f"({section_number})",
                        "text": content,
                        "type": SectionType.PARENTHESIS_NUMBER,
                        "children": []
                    }
                    
                    # Add to parent
                    parent_section["children"].append(new_section)
                    
                    # Update tracking variables
                    current_section_type = SectionType.PARENTHESIS_NUMBER
                    section_text = content
                    last_section = new_section
                    
                    # Move to next paragraph
                    i += 1
                    continue
            
            # Check if this paragraph starts a section at a higher level
            if self._is_higher_level_section(section_type, parent_section["type"]):
                # Finalize the current section if necessary
                if current_section_type is not None and last_section is not None:
                    last_section["text"] = section_text.strip()
                
                # Return to let the higher level handle this paragraph
                return i
            
            # If it's not a new section at this level or a higher level,
            # it's either content for the current section or a lower level
            if current_section_type is not None and last_section is not None:
                # Try to process lower level sections
                new_index = self._analyze_sections(paragraphs, last_section, i)
                
                # If the index didn't change, it's not a lower level section,
                # so we add it to the current section's text
                if new_index == i:
                    section_text += "\n" + paragraph
                    i += 1
                else:
                    i = new_index
            else:
                # This paragraph doesn't match any section pattern we're looking for,
                # so just add it to the parent's text
                if parent_section["text"]:
                    parent_section["text"] += "\n" + paragraph
                else:
                    parent_section["text"] = paragraph
                i += 1
        
        # Finalize the last section if necessary
        if current_section_type is not None and last_section is not None:
            last_section["text"] = section_text.strip()
            
        return i
    
    def _is_higher_level_section(self, section_type: SectionType, parent_type: SectionType) -> bool:
        """
        Checks if a section type is at a higher level than the parent section type
        
        Parameters:
            section_type: The section type to check
            parent_type: The parent section type
            
        Returns:
            Whether the section being checked is at a higher level
        """
        # Define hierarchy
        hierarchy = [
            SectionType.MAIN,
            SectionType.NUMBERED,
            SectionType.HEBREW_LETTER,
            SectionType.PARENTHESIS_NUMBER
        ]
        
        # Get indices in hierarchy
        try:
            section_index = hierarchy.index(section_type)
            parent_index = hierarchy.index(parent_type)
            
            # Lower index means higher in hierarchy
            return section_index < parent_index
        except ValueError:
            # If type not found in hierarchy, default to False
            return False 