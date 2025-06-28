import pdfplumber

def extract_text_from_pdf(pdf_path: str):
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"
    return all_text.strip()