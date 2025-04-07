#!/usr/bin/env python3
import os
import re
from services.nikud_service import NikudService
from services.document_processor import DocumentProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hebrew letters for section headers
hebrew_letters = [
    'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י',
    'יא', 'יב', 'יג', 'יד', 'טו', 'טז', 'יז', 'יח', 'יט',
    'כ', 'כא', 'כב', 'כג', 'כד', 'כה', 'כו', 'כז', 'כח', 'כט',
    'ל', 'לא', 'לב', 'לג', 'לד', 'לה', 'לו', 'לז', 'לח', 'לט', 
    'מ', 'מא', 'מב', 'מג', 'מד', 'מה', 'מו', 'מז', 'מח', 'מט'
]

def find_header_patterns(text, filename):
    """Find patterns that might contain section headers in the text"""
    # Patterns to look for
    # 1. <b>{hebrew_letter}הקדושה...</b> - Hebrew letter followed immediately by text
    # 2. <b>{hebrew_letter}</b> - Just a Hebrew letter in bold
    # 3. Hebrew letter alone on a line
    
    sections_found = []
    
    # Split text into paragraphs
    paragraphs = text.split('\n')
    print(f"[{filename}] Found {len(paragraphs)} paragraphs")
    
    # Generate regex pattern to match Hebrew letters
    hebrew_letters_pattern = '|'.join(hebrew_letters)
    
    # Pattern 1: <b> followed by Hebrew letter at the start then text without space
    pattern1 = re.compile(f'<b>({hebrew_letters_pattern})([א-ת]+)')
    
    # Pattern 2: Hebrew letter alone in bold
    pattern2 = re.compile(f'<b>({hebrew_letters_pattern})</b>')
    
    # Pattern 3: Hebrew letter alone in a line (no HTML)
    pattern3 = re.compile(f'^({hebrew_letters_pattern})$')
    
    # Count of lines with <b> tag
    bold_lines = 0
    
    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()
        if not para_stripped:
            continue
        
        # Track if line has bold formatting
        if '<b>' in para:
            bold_lines += 1
        
        # Check for Pattern 1
        match1 = pattern1.search(para)
        if match1:
            letter = match1.group(1)
            next_word = match1.group(2)
            print(f"[{filename}] Line {i+1}: Found Pattern 1 - '{letter + next_word}' (starts with: '{letter}')")
            sections_found.append((i+1, para, letter, "pattern1"))
            continue
        
        # Check for Pattern 2
        match2 = pattern2.search(para)
        if match2:
            letter = match2.group(1)
            print(f"[{filename}] Line {i+1}: Found Pattern 2 - Just letter '{letter}'")
            sections_found.append((i+1, para, letter, "pattern2"))
            continue
        
        # Check for Pattern 3 (standalone Hebrew letter)
        match3 = pattern3.match(para_stripped)
        if match3:
            letter = match3.group(1)
            print(f"[{filename}] Line {i+1}: Found Pattern 3 - Standalone letter '{letter}'")
            sections_found.append((i+1, para, letter, "pattern3"))
            continue
        
        # Check for any bold text that starts with a Hebrew letter
        if '<b>' in para:
            start_idx = para.find('<b>') + 3
            end_idx = para.find('</b>', start_idx)
            if end_idx > start_idx:
                bold_content = para[start_idx:end_idx]
                # Check if it starts with a Hebrew letter
                if bold_content and '\u0590' <= bold_content[0] <= '\u05FF':
                    print(f"[{filename}] Line {i+1}: Found bold text starting with Hebrew letter: '{bold_content[:20]}...'")
                    hebrew_char = bold_content[0]
                    sections_found.append((i+1, para, hebrew_char, "bold_hebrew"))
    
    # Count by letter
    letter_counts = {}
    for _, _, letter, _ in sections_found:
        letter_counts[letter] = letter_counts.get(letter, 0) + 1
    
    print(f"\n[{filename}] Found {len(sections_found)} potential section headers")
    print(f"[{filename}] Total paragraphs with <b> tags: {bold_lines}")
    print(f"\n[{filename}] Letter distribution:")
    for letter, count in sorted(letter_counts.items()):
        print(f"  {letter}: {count}")
    
    return sections_found

def find_raw_header_patterns(paragraphs, filename):
    """Find patterns that might contain section headers in raw paragraphs"""
    sections_found = []
    
    print(f"[{filename}] Analyzing {len(paragraphs)} raw paragraphs")
    
    for i, para in enumerate(paragraphs):
        para_stripped = para.strip()
        if not para_stripped:
            continue
        
        # Check if this is a standalone Hebrew letter
        if para_stripped in hebrew_letters:
            print(f"[{filename}] Line {i+1}: Found standalone Hebrew letter: '{para_stripped}'")
            sections_found.append((i+1, para, para_stripped, "raw_standalone"))
            continue
            
        # Check for pattern like טהקדושה (Hebrew letter followed by text without space)
        for marker in hebrew_letters:
            if para_stripped.startswith(marker) and len(para_stripped) > len(marker):
                # Check if the next character after marker is a Hebrew letter
                next_char_pos = len(marker)
                if next_char_pos < len(para_stripped) and '\u0590' <= para_stripped[next_char_pos] <= '\u05FF':
                    print(f"[{filename}] Line {i+1}: Found Hebrew letter + text: '{para_stripped[:20]}...'")
                    sections_found.append((i+1, para, marker, "raw_letter_text"))
                    break
    
    # Count by letter
    letter_counts = {}
    for _, _, letter, _ in sections_found:
        letter_counts[letter] = letter_counts.get(letter, 0) + 1
    
    print(f"\n[{filename}] Found {len(sections_found)} potential section headers in raw paragraphs")
    print(f"\n[{filename}] Raw letter distribution:")
    for letter, count in sorted(letter_counts.items()):
        print(f"  {letter}: {count}")
    
    return sections_found

def main():
    source_file = "source.docx"
    target_file = "target.docx"
    
    if not os.path.exists(source_file):
        print(f"Source file not found: {source_file}")
    
    if not os.path.exists(target_file):
        print(f"Target file not found: {target_file}")
        return
    
    nikud_service = NikudService()
    doc_processor = DocumentProcessor()
    
    # Compare document processing in both source and target files
    if os.path.exists(source_file):
        print(f"\n===== Analyzing SOURCE file: {source_file} =====")
        
        # Read as raw paragraphs
        source_paragraphs, source_doc = nikud_service._read_docx_raw(source_file)
        
        # Analyze raw paragraphs
        print("\n----- Raw Paragraph Analysis -----")
        raw_source_sections = find_raw_header_patterns(source_paragraphs, "SOURCE_RAW")
        
        # Split to sections using raw approach
        print("\n----- Raw DocumentProcessor Analysis -----")
        raw_processor_sections = doc_processor.split_to_sections_from_raw(source_paragraphs)
        print(f"SOURCE RAW: DocumentProcessor found {len(raw_processor_sections)} sections")
        print("SOURCE RAW section headers:")
        for section in raw_processor_sections:
            print(f"  - {section.header}")
            
        # Now process with HTML method
        source_text, _ = nikud_service._read_docx(source_file)
        
        # Analyze with HTML/pattern approach
        print("\n----- HTML/Pattern Analysis -----")
        source_sections = find_header_patterns(source_text, "SOURCE")
        
        # Split to sections using original method
        print("\n----- HTML DocumentProcessor Analysis -----")
        html_processor_sections = doc_processor.split_to_sections(source_text)
        print(f"SOURCE HTML: DocumentProcessor found {len(html_processor_sections)} sections")
        print("SOURCE HTML section headers:")
        for section in html_processor_sections:
            print(f"  - {section.header}")
    
    print(f"\n===== Analyzing TARGET file: {target_file} =====")
    
    # Read as raw paragraphs
    target_paragraphs, target_doc = nikud_service._read_docx_raw(target_file)
    
    # Analyze raw paragraphs
    print("\n----- Raw Paragraph Analysis -----")
    raw_target_sections = find_raw_header_patterns(target_paragraphs, "TARGET_RAW")
    
    # Split to sections using raw approach
    print("\n----- Raw DocumentProcessor Analysis -----")
    raw_target_processor_sections = doc_processor.split_to_sections_from_raw(target_paragraphs)
    print(f"TARGET RAW: DocumentProcessor found {len(raw_target_processor_sections)} sections")
    print("TARGET RAW section headers:")
    for section in raw_target_processor_sections:
        print(f"  - {section.header}")
    
    # Now process with HTML method
    target_text, _ = nikud_service._read_docx(target_file)
    
    # Analyze with HTML/pattern approach
    print("\n----- HTML/Pattern Analysis -----")
    target_sections = find_header_patterns(target_text, "TARGET")
    
    # Split to sections using original method
    print("\n----- HTML DocumentProcessor Analysis -----")
    html_target_processor_sections = doc_processor.split_to_sections(target_text)
    print(f"TARGET HTML: DocumentProcessor found {len(html_target_processor_sections)} sections")
    print("TARGET HTML section headers:")
    for section in html_target_processor_sections:
        print(f"  - {section.header}")
    
    # Extract sample lines from target file to understand the format
    print("\n===== Sample paragraphs from TARGET file =====")
    for i, para in enumerate(target_paragraphs[:20]):  # Show first 20 paragraphs
        if para.strip():
            print(f"Line {i+1}: {para[:100]}...")

if __name__ == "__main__":
    main() 