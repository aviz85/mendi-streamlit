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
    # Print the exact line with its representation for debugging
    print(f"Checking line: '{line}'")
    print(f"Line in bytes: {line.encode('utf-8')}")
    
    # Remove whitespace
    line = line.strip()
    
    # Debug raw line content
    print(f"Stripped line: '{line}'")
    print(f"Length: {len(line)}")
    print(f"Characters: {[c for c in line]}")
    
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
        print(f"Direct match with known marker: {line}")
        result = True
        print(f"Is Hebrew letter line? {result}\n")
        return result
    
    # Remove any punctuation or non-letter characters
    cleaned_line = re.sub(r'[^\u0590-\u05FF]', '', line)
    print(f"Cleaned line (Hebrew chars only): '{cleaned_line}'")
    
    # Check if the cleaned line matches a known marker
    if cleaned_line in hebrew_section_markers:
        print(f"Found marker after cleaning: '{line}' → '{cleaned_line}'")
        result = True
        print(f"Is Hebrew letter line? {result}\n")
        return True
    
    # Extract only Hebrew characters
    hebrew_chars = ''.join(c for c in line if '\u0590' <= c <= '\u05FF')
    print(f"Hebrew characters only: '{hebrew_chars}' (length: {len(hebrew_chars)})")
    
    # Check if we have 1-3 Hebrew letters
    if 1 <= len(hebrew_chars) <= 3:
        print(f"Found 1-3 Hebrew letters in: '{line}'")
        result = True
        print(f"Is Hebrew letter line? {result}\n")
        return True
    
    # Original check
    hebrew_pattern = re.compile(r'^[\u0590-\u05FF]{1,3}$')
    result = bool(hebrew_pattern.match(line))
    
    print(f"Is Hebrew letter line? {result}\n")
    return result

def analyze_document(text):
    """Analyze document content and look for section headers"""
    print("===== DOCUMENT ANALYSIS =====")
    
    # Split lines
    lines = text.split('\n')
    print(f"Total lines: {len(lines)}")
    
    # Count potential section headers
    section_headers = []
    
    for i, line in enumerate(lines):
        if line.strip():  # Skip empty lines
            if is_hebrew_letter_line(line):
                section_headers.append((i+1, line))
    
    print(f"\nFound {len(section_headers)} potential section headers:")
    for line_num, header in section_headers:
        print(f"Line {line_num}: '{header}'")
    
    # Analyze lines around potential section delimiters
    print("\n===== CONTEXT ANALYSIS =====")
    for line_num, header in section_headers:
        context_start = max(0, line_num - 3)
        context_end = min(len(lines), line_num + 2)
        
        print(f"\nContext around '{header}' (line {line_num}):")
        for i in range(context_start, context_end):
            prefix = ">" if i+1 == line_num else " "
            print(f"{prefix} Line {i+1}: '{lines[i]}'")

def debug_hebrew_detection():
    """Test the Hebrew detection function with various inputs"""
    print("===== HEBREW DETECTION TEST =====")
    test_cases = [
        "א",
        "ב",
        "א.",
        "<b>א</b>",
        " א ",
        "א ב",  # Two Hebrew letters with space
        "ב ג", # Another two Hebrew letters with space
        "א-ב", # Two Hebrew letters with hyphen
        "יא", # Two Hebrew letters together
        "כב", # Two Hebrew letters together
        "אבג",
        "test",
        "א test",
    ]
    
    for test in test_cases:
        print(f"Testing: '{test}'")
        result = is_hebrew_letter_line(test)
        print(f"Result: {result}\n")

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "target.docx"
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    print(f"Analyzing file: {file_path}")
    
    text, doc = read_docx(file_path)
    if text:
        # Run analysis
        analyze_document(text)
        
        # Test Hebrew detection
        debug_hebrew_detection()

if __name__ == "__main__":
    main() 