from app.openai_utils import ask_gpt
from app.pdf_utils import extract_items_from_pdf_ai

def extract_by_instructions(pdf_path: str, instruction: str) -> list[str]:
    text = extract_items_from_pdf_ai(pdf_path)

    prompt = f"""
    You are a smart AI assistant that extracts information from documents.

The user uploaded a PDF and gave this instruction:
\"\"\"
{instruction}
\"\"\"

Here is the full text of the PDF:
\"\"\"
{text}
\"\"\"

Please follow the instruction carefully and return a structured answer in plain text or JSON.
"""

    return ask_gpt(prompt)
    """"""