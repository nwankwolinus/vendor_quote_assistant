import os
from dotenv import load_dotenv
import gspread 
from google.oauth2.service_account import Credentials
from fastapi import HTTPException

load_dotenv()

#set up your sheet name
SHEET_NAME = "Vendor_Quotes"

# Define the scope
def get_sheet():

    #scope
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Load credential_path and sheet_id from .env file
    creds_path = os.getenv("GOOGLE_CREDS_PATH")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not creds_path or not sheet_id:
        raise HTTPException(status_code=500, detail="Google credentials or sheet ID not set in environment variables.")
    
    # Add your credentials file here
    creds = Credentials.from_service_account_file(creds_path,scopes=scopes)

    # Authorize the client sheet
    client = gspread.authorize(creds)

    
    # Open the sheet
    sheet = client.open_by_key(sheet_id).sheet1

    # Return the sheet
    return sheet

# save quote_to_sheet
def save_quote_to_sheet(quote):
    sheet = get_sheet() 
    try:
        sheet.append_row([
            quote["vendor"],
            quote["item"],
            quote["model"],
            quote["manufacturer"],
            str(quote["price"]),
            str(quote["quantity"]),
            quote["date"] 
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving quote to sheet: {e}")
    
# Function to read quotes from the sheet
def read_quotes_from_sheet():
    sheet = get_sheet()
    # Get all records from the sheet
    records = sheet.get_all_records()
    return records

# Define the function recommender function
def recommend_vendor(item_name: str):
    quotes = read_quotes_from_sheet()
    item_quotes = [q for q in quotes if q['item'].lower() == item_name.lower()]

    if not item_quotes:
        raise HTTPException(status_code=404, detail="No quotes found for the specified item.")
    
    best_quote = min(item_quotes, key=lambda x: float(x['price']))
    return f"The best vendor for {item_name} is {best_quote['vendor']} with a price of {best_quote['vendor']}"

# Check for duplicate quotes
def is_duplicate_quote(item, existing_records):
    for record in existing_records:
        if (
            str(record.get("vendor", "")).strip().lower() == str(item["vendor"]).strip().lower() and
            str(record.get("item", "")).strip().lower() == str(item["item"]).strip().lower() and
            str(record.get("model", "")).strip().lower() == str(item["model"]).strip().lower() and
            str(record.get("manufacturer", "")).strip().lower() == str(item["manufacturer"]).strip().lower() and
            str(record.get("price", "")).replace(",", "") == str(item["price"]) and
            str(record.get("date", "")).strip() == str(item["date"]).strip()
        ):
            return True
    return False

def bulk_save_to_sheet(items):
    sheet = get_sheet()
    existing_records = sheet.get_all_records()

    saved = 0
    rows_to_insert = []
    skipped_duplicates = []

    for item in items:
        if is_duplicate_quote(item, existing_records):
            skipped_duplicates.append(item)
            continue

        row = [
            item["vendor"],
            item["item"],
            item["model"],  # Includes the kA rating
            item["manufacturer"],
            str(item["price"]),
            str(item.get("quantity", 1)),
            item.get("date", "")
        ]
        rows_to_insert.append(row)

    try:
        if rows_to_insert:
            sheet.append_rows(rows_to_insert)
            saved = len(rows_to_insert)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving batch to sheet: {e}")

    return {
        "saved_count": saved,
        "skipped_duplicates": skipped_duplicates
    }

def save_quote_to_sheet(quote):
    sheet = get_sheet() 
    try:
        sheet.append_row([
            quote["vendor"],
            quote["item"],
            quote["model"],  # Includes kA rating
            quote["manufacturer"],
            str(quote["price"]),
            str(quote.get("quantity", 1)),
            quote.get("date", "")
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving quote to sheet: {e}")
