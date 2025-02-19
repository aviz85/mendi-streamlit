from docx import Document
import sys
import re

def clean_bold_tags(text: str) -> str:
    """Clean and optimize bold tags:
    1. Remove empty bold tags
    2. Merge adjacent bold tags
    3. Remove redundant spaces between merged tags
    """
    # Remove empty bold tags
    text = re.sub(r'<b>\s*</b>', '', text)
    
    # Initial cleanup - normalize spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Merge adjacent bold tags (including when only spaces between them)
    while True:
        # Try to find and merge adjacent tags
        new_text = re.sub(r'</b>(\s*)<b>', r'\1', text)
        if new_text == text:  # No more merges possible
            break
        text = new_text
    
    return text.strip()

def analyze_docx_bold(file_path: str):
    """Analyze bold formatting in DOCX and output HTML-style text"""
    doc = Document(file_path)
    result = []
    
    print("\n=== ניתוח פורמט מודגש ===")
    print(f"קובץ: {file_path}")
    print("-------------------")
    
    for i, para in enumerate(doc.paragraphs, 1):
        para_text = ""
        has_bold = False
        
        for run in para.runs:
            if run.bold:
                para_text += f"<b>{run.text}</b>"
                has_bold = True
            else:
                para_text += run.text
        
        if has_bold:
            # Clean up bold tags
            cleaned_text = clean_bold_tags(para_text)
            if '<b>' in cleaned_text:  # Only add if still has bold after cleanup
                result.append(f"פסקה {i}:")
                result.append(cleaned_text)
                result.append("לפני ניקוי:")
                result.append(para_text)
                result.append("-------------------")
    
    if not result:
        print("לא נמצאו חלקים מודגשים במסמך")
    else:
        print("\n".join(result))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_docx_bold.py <path_to_docx>")
        sys.exit(1)
        
    analyze_docx_bold(sys.argv[1]) 