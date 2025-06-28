from fastapi import APIRouter, HTTPException, Query, UploadFile, File
import shutil
from fastapi.responses import JSONResponse
from app.openai_utils import ask_gpt, recommend_best_vendor
from app.model import Quote
# from app.storage import save_quotes_to_csv, load_quotes_from_csv
from app.google_sheet_utils import save_quote_to_sheet, read_quotes_from_sheet
import os
from app.ai_invoice_extractor import extract_text_from_pdf
import json
import re
from datetime import date

router = APIRouter()

# quote_db = load_quotes_from_csv()

@router.get("/")
def root():
    return {"message":"Vendor Quotation Assistant"}

@router.post("/ask")
def chat_with_bot(prompt: str):
    response = ask_gpt(prompt)
    return {"response": response}

@router.post("/quotes", response_model=dict)
def submit_quote(quote: Quote):
    print("Incoming Quote:", quote)
    try:
        save_quote_to_sheet(quote)
        return {"message": "Quote saved to Google Sheet successfully", "quote": quote}
    except Exception as e:
        print("Error during saving:", e)
        raise HTTPException(status_code=500, detail=f"Failed to save quote: {str(e)}")

@router.get("/quotes")
def get_all_quotes():
    try:
        quotes = read_quotes_from_sheet()
        if not quotes:
            raise HTTPException(status_code=404, detail="No quotes available in Google Sheet")
        return {"quotes": quotes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quotes: {str(e)}")
    
@router.get("/recommend")
def get_recommendation(item_name: str = Query(..., description="Name of the item to get vendor recommendation for")):
    try:
        recommendation = recommend_best_vendor(item_name)
        return {"recommendation": recommendation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation: {str(e)}")
    
@router.post("/upload_invoice_ai")
def upload_invoice_ai(file: UploadFile = File(...)):
    try:
        # Ensure the temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        # Save the uploaded file to into /temp directory
        temp_path = f"temp/{file.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # extract raw text from the PDF
        raw_text = extract_text_from_pdf(temp_path)

        #GPT prompt
        prompt = f"""
        Today is {date.today().isoformat()}.
You are an AI assistant specialized in reading and structuring invoice documents.

Your task is to analyze the following **raw text extracted from a vendor's invoice PDF** and return a **well-structured JSON object** with the following fields:

- "vendor_name": Name of the company issuing the invoice
- "invoice_date": The date on the invoice or PO
- "items": A list of items, where each item contains:
  - "description": Description of the item
  - "quantity": Number of units
  - "unit_price": Price per unit
  - "total_price": Total for that line
- "total_before_vat": Total cost before VAT is added
- "vat_amount": Value-added tax (VAT) amount
- "discount": Any discount applied (if any, else 0)
- "grand_total": Final total after applying VAT and discount

Important Instructions:
- Respond **only in JSON format** (no markdown or explanation).
- If something is missing, provide `null` or `"Not found"` instead of skipping the field.
- If no items are found, return `"items": []` but still return the other fields.
- Keep all number values as **plain numbers** (no commas, currency symbols, or formatting).
- All keys must be **lowercase with underscores**, not camelCase or natural text.
- Do not wrap the response in markdown backticks.

---

Here is the extracted text from the invoice:
{raw_text}
---
"""
        structured_result = ask_gpt(prompt)

        # Clean GPT's markdown backticks and parse to real dict
        try:
            json_str = re.sub(r"^```json|```$", "", structured_result.strip(), flags=re.MULTILINE)
            invoice_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"GPT response was not valid json: {e}")
        
        # save each item to Google Sheet
        saved_items = []
        for item in invoice_data["items"]:
            quote = {
                "vendor": invoice_data["vendor_name"],
                "item": item["description"],
                "price": item["unit_price"],
                "quantity": item["quantity"],
                "date": invoice_data["invoice_date"]
            }
            save_quote_to_sheet(quote)
            saved_items.append(quote)

        # Clean up the temporary file
        os.remove(temp_path)

        return{
            "message": "Invoice data extracted and saved successfully",
            "vendor": invoice_data["vendor_name"],
            "items_saved": len(saved_items),
            "sample": saved_items[:3]
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract invoice data: {e}")
        



