from docx import Document
from docx.shared import RGBColor, Pt
from docx.oxml import OxmlElement

def analyze_docx_deeply(docx_path, start=50, end=100):
    doc = Document(docx_path)
    
    for i, paragraph in enumerate(doc.paragraphs[start-1:end], start):
        print(f"\n{'='*80}")
        print(f"פסקה מספר {i}")
        print(f"טקסט: {paragraph.text}")
        
        # ניתוח סגנון הפסקה
        print("\nסגנון פסקה:")
        style = paragraph.style
        print(f"שם הסגנון: {style.name}")
        
        # ניתוח יישור וריווח
        para_format = paragraph.paragraph_format
        if para_format:
            print("\nפורמט פסקה:")
            alignment = str(paragraph.alignment) if paragraph.alignment else "לא מוגדר"
            print(f"יישור: {alignment}")
            if para_format.line_spacing:
                print(f"ריווח שורות: {para_format.line_spacing}")
            if para_format.space_before:
                print(f"רווח לפני: {para_format.space_before.pt}pt")
            if para_format.space_after:
                print(f"רווח אחרי: {para_format.space_after.pt}pt")

        # ניתוח XML מלא
        if hasattr(paragraph, '_p'):
            p = paragraph._p
            print("\nXML מאפייני פסקה:")
            if p.pPr is not None:
                for child in p.pPr:
                    print(f"תג: {child.tag.split('}')[-1]}")
                    for key, value in child.attrib.items():
                        print(f"  {key}: {value}")

        # ניתוח מפורט של כל run
        print("\nניתוח runs:")
        for idx, run in enumerate(paragraph.runs):
            print(f"\nRun {idx+1}:")
            print(f"טקסט: {run.text}")
            
            # תכונות בסיסיות
            properties = {
                'bold': run.bold,
                'italic': run.italic,
                'underline': run.underline,
                'strike': run.font.strike,
                'subscript': run.font.subscript,
                'superscript': run.font.superscript,
                'caps': run.font.all_caps,
                'small_caps': run.font.small_caps,
                'shadow': run.font.shadow
            }
            
            print("תכונות בסיסיות:")
            for prop, value in properties.items():
                if value is not None:
                    print(f"  {prop}: {value}")
            
            # תכונות גופן
            font = run.font
            print("תכונות גופן:")
            if font.name:
                print(f"  שם גופן: {font.name}")
            if font.size:
                print(f"  גודל: {font.size.pt}pt")
            if font.color.rgb:
                print(f"  צבע: {font.color.rgb}")
            
            # XML של ה-run
            if hasattr(run, '_r'):
                r = run._r
                print("XML תכונות:")
                if r.rPr is not None:
                    for child in r.rPr:
                        print(f"  תג: {child.tag.split('}')[-1]}")
                        for key, value in child.attrib.items():
                            print(f"    {key}: {value}")

try:
    file_path = "example.docx"  # שם הקובץ שלך
    analyze_docx_deeply(file_path)
except Exception as e:
    print(f"אירעה שגיאה: {str(e)}")