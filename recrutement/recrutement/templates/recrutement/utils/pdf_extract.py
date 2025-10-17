# recrutement/utils/pdf_extract.py
from pdfminer.high_level import extract_text

def extract_pdf_text(file_path):
    try:
        text = extract_text(file_path)
        return text
    except Exception as e:
        return ""
