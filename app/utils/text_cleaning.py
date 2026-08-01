import re
import unicodedata

def clean_text(text: str) -> str:
    """Clean and normalize extracted text, removing OCR artifacts and weird unicode characters."""
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    
    # Replace non-standard bullets with standard hyphen
    text = re.sub(r'[\u2022\u2023\u25B6\u25C0\u2013\u2014\u25cf\u25cb\u25a0\u25a1]', '-', text)
    
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Clean OCR noise: strings of repetitive non-alphanumeric chars
    text = re.sub(r'([_\-=\*\.#]){4,}', r'\1\1', text)
    
    # Ensure newline consistency
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def split_into_bullets(text: str) -> list:
    """Split text into individual bullet points or sentences for granular evaluation."""
    if not text:
        return []
    
    lines = text.split('\n')
    bullets = []
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        
        # Remove leading bullet symbols or numbers
        cleaned_line = re.sub(r'^(?:[\-\*\•]|(?:\d+[\.\)]))\s*', '', cleaned_line)
        if len(cleaned_line) > 5:
            bullets.append(cleaned_line)
            
    return bullets
