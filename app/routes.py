from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from app.openai_utils import ask_gpt, recommend_best_vendor
from app.model import Quote
# from app.storage import save_quotes_to_csv, load_quotes_from_csv
from app.google_sheet_utils import save_quote_to_sheet, read_quotes_from_sheet, bulk_save_to_sheet
import os
from app.pdf_utils import extract_items_from_pdf_ai

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
            f.write(file.file.read())
        
        extract_items = extract_items_from_pdf_ai(temp_path)
        saved_accounts = bulk_save_to_sheet(extract_items)

        os.remove(temp_path) # Clean up the temporary file)

        return {
            "message": f" Extracted {len(extract_items)} items. Saved {saved_accounts} items to Google Sheet.",
            "sample": extract_items[:3] # Return first 3 items as sample
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")




