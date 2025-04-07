"""
Text patterns for document processing

This module contains definitions of text patterns used for identifying sections, headers, 
and text structures in documents. It provides functions for detecting sections and their types.
"""

import re
import enum
from typing import Optional, Match, List, Dict, Any

class SectionType(enum.Enum):
    """Enumeration of section types in legal documents"""
    CHAPTER = "CHAPTER"        # פרק
    ARTICLE = "ARTICLE"        # סעיף
    SUB_ARTICLE = "SUB_ARTICLE"  # תת-סעיף
    PARAGRAPH = "PARAGRAPH"    # פסקה
    UNKNOWN = "UNKNOWN"        # לא ידוע

# Regular expression patterns for identifying sections
SECTION_PATTERNS = {
    # Chapter pattern (e.g., "פרק א':", "פרק 1:", etc.)
    SectionType.CHAPTER: re.compile(r'^פרק\s+([א-ת]\'|[א-ת]|[0-9]+)\s*:(.*)$'),
    
    # Article pattern (e.g., "1.", "א.", etc.)
    SectionType.ARTICLE: re.compile(r'^([0-9]+|[א-ת])\.\s+(.*)$'),
    
    # Sub-article pattern (e.g., "(1)", "(א)", etc.)
    SectionType.SUB_ARTICLE: re.compile(r'^\(([0-9]+|[א-ת])\)\s+(.*)$'),
    
    # Paragraph pattern (e.g., "1)", "א)", etc.)
    SectionType.PARAGRAPH: re.compile(r'^([0-9]+|[א-ת])\)\s+(.*)$'),
}

def detect_section_type(text: str) -> tuple[Optional[SectionType], Optional[Match]]:
    """
    Detect the type of section based on its text
    
    Parameters:
        text: The text to analyze
        
    Returns:
        A tuple containing the section type and regex match object (or None, None if not a section)
    """
    # Check against all patterns
    for section_type, pattern in SECTION_PATTERNS.items():
        match = pattern.match(text)
        if match:
            return section_type, match
    
    # No match found
    return None, None

def is_section_header(text: str) -> bool:
    """
    Check if a text is a section header
    
    Parameters:
        text: The text to check
        
    Returns:
        True if the text is a section header, False otherwise
    """
    section_type, _ = detect_section_type(text)
    return section_type is not None

def extract_section_info(text: str) -> Dict[str, Any]:
    """
    Extract information from a section header
    
    Parameters:
        text: The section header text
        
    Returns:
        A dictionary containing section information (type, number, title, etc.)
    """
    section_type, match = detect_section_type(text)
    
    if not section_type or not match:
        return {
            "type": SectionType.UNKNOWN,
            "number": None,
            "title": None,
            "text": text
        }
    
    # Extract number and title from match
    number = match.group(1)
    title_text = match.group(2).strip() if len(match.groups()) > 1 else ""
    
    return {
        "type": section_type,
        "number": number,
        "title": f"{get_section_type_prefix(section_type)} {number}{':' if title_text else ''}",
        "text": title_text,
        "full_text": text
    }

def get_section_type_prefix(section_type: SectionType) -> str:
    """
    Get the Hebrew prefix for a section type
    
    Parameters:
        section_type: The section type
        
    Returns:
        The Hebrew prefix for the section type
    """
    prefixes = {
        SectionType.CHAPTER: "פרק",
        SectionType.ARTICLE: "",
        SectionType.SUB_ARTICLE: "",
        SectionType.PARAGRAPH: "",
        SectionType.UNKNOWN: "",
    }
    return prefixes.get(section_type, "") 