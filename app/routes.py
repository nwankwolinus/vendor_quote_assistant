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
You are an invoice processing assistant.

Extract the following details this vendor invoice text:

1. Vendor name
2. Invoice or PO date
3. A list of items (description, quantity, unit price, total price)
4. Total before VAT
5. VAT amount
6. Discount
7. Grand total

Response in JSON format

---
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

        # Clean up the temporary file
        os.remove(temp_path)

        return{"extracted_invoice": invoice_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract invoice data: {e}")
        



