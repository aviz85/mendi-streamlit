#!/usr/bin/env python3
import os
import logging
from services.document_processor import DocumentProcessor, Section
from services.nikud_service import NikudService

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Test the document processor on the target document"""
    dp = DocumentProcessor()
    nikud_service = NikudService()  # Create instance of NikudService
    
    file_path = "target.docx"
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    print(f"Processing document: {file_path}")
    
    # Read document using NikudService
    text, _ = nikud_service._read_docx(file_path)
    
    # Print sample of the text to inspect
    print("\nSample of the document text:")
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if i < 20:  # Print first 20 lines
            print(f"Line {i+1}: '{line}'")
        elif i > 60 and i < 80:  # Print sample from middle
            print(f"Line {i+1}: '{line}'")
        if i >= 80:
            break
    print("...")
    
    # Find section headers
    paragraphs = text.split('\n')
    headers = []
    
    for i, para in enumerate(paragraphs):
        if dp._is_hebrew_letter_line(para):
            headers.append((i+1, para))
    
    print(f"\nFound {len(headers)} potential section headers:")
    
    # Print first 10 headers for quick check
    for i, (line_num, header) in enumerate(headers):
        if i < 10:
            # Extract only Hebrew characters for clarity
            hebrew_only = ''.join(c for c in header if '\u0590' <= c <= '\u05FF')
            print(f"Line {line_num}: '{header}' (Hebrew content: '{hebrew_only}')")
    
    print("...")
    
    # Count section headers by letter length
    letter_counts = {}
    for _, header in headers:
        hebrew_chars = ''.join(c for c in header if '\u0590' <= c <= '\u05FF')
        count = len(hebrew_chars)
        letter_counts[count] = letter_counts.get(count, 0) + 1
    
    print("\nSection headers summary:")
    print(f"Total sections found: {len(headers)}")
    
    for count, quantity in sorted(letter_counts.items()):
        print(f"  Headers with {count} Hebrew letters: {quantity}")
    
    # Process full document to sections
    sections = dp.split_to_sections(text)
    print(f"\nDocument was split into {len(sections)} sections")
    
    # Print first few sections
    for i, section in enumerate(sections[:3]):
        print(f"\nSection {i+1}: {section.header}")
        content_preview = section.content[:100] + "..." if len(section.content) > 100 else section.content
        print(f"Content preview: {content_preview}")

if __name__ == "__main__":
    main() 