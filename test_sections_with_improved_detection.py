import os
import logging
import re
import sys
from docx import Document
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def read_docx(file_path):
    """Read DOCX file and return text content"""
    try:
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text), doc
    except Exception as e:
        logger.error(f"Error reading DOCX file: {e}")
        return None, None

def is_hebrew_letter_line(line):
    """Check if line contains only 1-3 Hebrew letters"""
    # Remove whitespace
    line = line.strip()
    
    # First, check for extremely short lines
    if not line:
        return False
    
    # Common section markers
    hebrew_section_markers = [
        'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י',
        'יא', 'יב', 'יג', 'יד', 'טו', 'טז', 'יז', 'יח', 'יט',
        'כ', 'כא', 'כב', 'כג', 'כד', 'כה', 'כו', 'כז', 'כח', 'כט',
        'ל', 'לא', 'לב', 'לג', 'לד', 'לה', 'לו', 'לז', 'לח', 'לט', 
        'מ', 'מא', 'מב', 'מג', 'מד', 'מה', 'מו', 'מז', 'מח', 'מט'
    ]
    
    # Quick check if this is a common section marker
    if line in hebrew_section_markers or line + '.' in hebrew_section_markers:
        return True

    # Remove any punctuation or non-letter characters
    cleaned_line = re.sub(r'[^\u0590-\u05FF]', '', line)
    
    # Check if the cleaned line matches a known marker
    if cleaned_line in hebrew_section_markers:
        return True
    
    # Extract only Hebrew characters
    hebrew_chars = ''.join(c for c in line if '\u0590' <= c <= '\u05FF')
    
    # Check if we have 1-3 Hebrew letters
    if 1 <= len(hebrew_chars) <= 3:
        return True
    
    # Original check as fallback
    clean_line = line.rstrip('.')
    hebrew_pattern = re.compile(r'^[\u0590-\u05FF]{1,3}$')
    return bool(hebrew_pattern.match(clean_line))

def find_section_headers(text):
    """Find all section headers in the text"""
    lines = text.split('\n')
    headers = []
    
    for i, line in enumerate(lines):
        if line.strip() and is_hebrew_letter_line(line):
            headers.append((i+1, line))
    
    return headers

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "source.docx"
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    print(f"Analyzing file: {file_path}")
    
    text, doc = read_docx(file_path)
    if text:
        headers = find_section_headers(text)
        
        print(f"\nFound {len(headers)} section headers:")
        for line_num, header in headers:
            # Extract only Hebrew characters for clarity
            hebrew_only = ''.join(c for c in header if '\u0590' <= c <= '\u05FF')
            print(f"Line {line_num}: '{header}' (Hebrew content: '{hebrew_only}')")
        
        print("\nSection headers summary:")
        print(f"Total sections found: {len(headers)}")
        
        # Count how many have 1, 2, or 3 Hebrew letters
        letter_counts = {}
        for _, header in headers:
            hebrew_chars = ''.join(c for c in header if '\u0590' <= c <= '\u05FF')
            count = len(hebrew_chars)
            letter_counts[count] = letter_counts.get(count, 0) + 1
        
        for count, quantity in sorted(letter_counts.items()):
            print(f"  Headers with {count} Hebrew letters: {quantity}")

if __name__ == "__main__":
    main() 