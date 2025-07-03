import fitz # PyMuPDF
import json, re
from datetime import date
from app.openai_utils import ask_gpt

def extract_pdf_pages(pdf_path):
    doc = fitz.open(pdf_path)
    return [page.get_text("text") for page in doc]

def build_prompt(page_text: str) -> str:
    today = date.today().isoformat()
    return f"""
Today is {date.today().isoformat()}.
You are an AI assistant extracting structured data from an invoice or quotation.

Return a JSON array of structured items. Each item should contain:

- **"vendor"**: The company issuing the quote (e.g., Mikano)
- **"item"**: General classification like "100A 3P MCCB", "160A 4P ACB", "65A 3P Contactor"
    - Must follow the format: "<Amperage> <Poles> <Type>" 
    - Infer "MCCB", "MCB", "ACB", or "Contactor" based on context
    - for ABB: the Amperage is under the "Ratings [A]" column, Tmax, are MCCBs,
- **"model"**: Full model name, **including kA rating or trip range**
    - e.g., "XT5N 630 Ekip Dip LS/I In=630 36kA", "A1A 125 TMF MCCB 32-320", "T5N 400 TMA 320-3200"
    - If kA rating is missing, still include "Unknown kA" or trip range
- **"manufacturer"**: Based on model prefix:
    - ACTI9, Easy9, DOMAE, NSX, CVS, EZC, MVS, NW → Schneider Electric
    - XT1–XT7, T1–T7, A0C, A1A, A2C, Tmax, S200, Emax, XT1to5, A2B,SH201, SH202, SH203 → ABB
    - NXB, DZ47, NB1, NXM → CHINT
    - If unclear, use "Unknown"
- **"price"**: Extract numeric value in NGN (Naira). If not clear, return "Unknown". Unit price as a number (remove commas or currency symbols)
- **"quantity"**: If specified, use it. Otherwise default to 1
- **"date"**: Use invoice or PO date if available, else use today’s date: `{{today}}`

**Special Rules:**
- If the vendor is CHINT and the unit price is in a column titled "经销商", it's in USD — convert it by multiplying by 1800
- All breakers should be classified into one of: MCCB, MCB, ACB, or Contactor — infer from model or description
- Append the kA rating into the model string directly (if found anywhere)
- Don’t return markdown, explanations, or text. Return **only valid JSON array**

Format: Return only a **JSON array** (no markdown, no explanation)
---
Text:
\"\"\"{page_text}\"\"\"
"""
def clean_and_parse_json_response(raw_response: str):
    json_match = re.search(r"\[\s*{.*?}\s*\]", raw_response, re.DOTALL)
    if not json_match:
        raise ValueError("No valid JSON array found in the response.")
    return json.loads(json_match.group(0))

def extract_items_from_pdf_ai(pdf_path: str):
    pages = extract_pdf_pages(pdf_path)
    all_items = []

    for idx, page_text in enumerate(pages):
        prompt = build_prompt(page_text)
        try:
            gpt_response = ask_gpt(prompt)
            items = clean_and_parse_json_response(gpt_response)
            all_items.extend(items)
        except Exception as e:
            print(f"Error processing page {idx + 1}: {e}")
            continue

    return all_items


