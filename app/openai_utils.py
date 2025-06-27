import os
from openai import OpenAI
from dotenv import load_dotenv
from app.google_sheet_utils import read_quotes_from_sheet
from datetime import date

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_gpt(message: str) -> str:
    response = client.chat.completions.create(
        model = "gpt-4o", 
           messages = [
               {"role": "system", "content": "You are a helpful assistant."},
               {"role": "user", "content": message}
           ],

           temperature = 0.7,  
            
    )
    return response.choices[0].message.content

def recommend_best_vendor(item_name: str):
        records = read_quotes_from_sheet()
        if not records:
              return "No quotes found in the sheet."
        
        print("Items found:", [r['item'] for r in records if 'item' in r])  # Debug
        
        formatted_quotes = "\n".join([
              f"Vendor: {records['vendor']}, Item: {records['item']}, Price: {records['price']}, Date: {records['date']}"
                for records in records if 'item' in records and records['item'].strip().lower() == item_name.strip().lower()
        ])

        if not formatted_quotes:
              return f"No valid quotes found for item: {item_name}."

        prompt = f"""
        Today is {date.today()}.
        Given the following quotes, recommend the best vendor for purchasing the item '{item_name}' and why?

        {formatted_quotes}
    
        please consider price, vendor name, and recentness of the quote. Respond in a professional manner.
        """

        return ask_gpt(prompt)