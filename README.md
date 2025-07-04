🧠 Vendor Quote Assistant – AI-Powered PDF Extraction API
An intelligent assistant built with FastAPI that extracts structured data from vendor quotations, purchase orders, or product catalogs in PDF format — using OpenAI GPT models and saves the output to Google Sheets for automated quotation tracking.

🛠️ Built for teams managing procurement, quotations, and engineering documentation — powered by AI.

✨ Features
✅ Upload any PDF invoice, quotation, or catalog
✅ Provide natural language instructions to guide the extraction
✅ Extracts fields like: vendor, item, model, part_number, price, date, etc.
✅ Infers product categories like Acti9, Easypact, CVS, NSX, etc.
✅ Saves extracted data automatically to Google Sheets
✅ Supports flexible instructions, no hardcoded logic
✅ Built with: FastAPI, OpenAI, PyMuPDF, Google Sheets API

🚀 Example Use Cases
🧾 Upload a quotation and extract all breaker models & prices

📦 Process a product catalog and map by product range

📄 Extract part numbers, vendors, and pricing into a sheet for analysis

📊 Automate procurement data entry from PDF documents

🧪 Example Instruction Prompts
txt
Copy
Edit
"Extract all accessories from this catalog. Vendor is Mikano. Use 'Description' as item, use the heading (e.g. Acti9, CVS, NSX) as model. Capture part number, price in NGN, and today's date."
txt
Copy
Edit
"Extract vendor name, item description, model range, price, and part number. Save in JSON. Use 'Easypact', 'CVS', etc. from the section headers as model."
📁 Folder Structure
pgsql
Copy
Edit
vendor_quote_assistant/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── routes.py               # API route definitions
│   ├── pdf_utils.py            # PDF processing + GPT extraction
│   ├── sheets_utils.py         # Google Sheets integration
│   ├── openai_utils.py         # GPT API wrapper
│   └── .env                    # API keys & environment variables
├── requirements.txt
└── README.md
🔧 Setup Instructions
1. Clone the Repo
bash
Copy
Edit
git clone https://github.com/yourusername/vendor_quote_assistant.git
cd vendor_quote_assistant
2. Create a Python Virtual Environment
bash
Copy
Edit
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Set Up Environment Variables
Create a .env file with the following:

env
Copy
Edit
OPENAI_API_KEY=your_openai_api_key
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_CREDENTIALS_PATH=service_account.json
5. Run the Server
bash
Copy
Edit
uvicorn app.main:app --reload
⚙️ API Endpoints
POST /upload-ai
Upload a PDF + (optional) instruction to extract custom fields.

Form Fields:
file: PDF file

instruction: (Optional) Natural language prompt

Example:
bash
Copy
Edit
curl -X POST http://localhost:8000/upload-ai \
  -F "file=@your_invoice.pdf" \
  -F "instruction=Extract vendor name as Mikano and use Description as item..."
🧠 Tech Stack
Tool	Purpose
FastAPI	API framework
OpenAI GPT	AI document understanding & parsing
PyMuPDF (fitz)	PDF text extraction
gspread + Google API	Write data to Google Sheets
Pydantic	Data modeling and validation

✅ Sample JSON Output
json
Copy
Edit
[
  {
    "vendor": "Mikano",
    "item": "AUXILIARY SWITCH O-F FOR C60/ID",
    "model": "Acti9",
    "manufacturer": "Schneider Electric",
    "price": 17930,
    "part_number": "A9A26924",
    "date": "2025-07-04"
  }
]
📊 Google Sheets Setup
Create a Google Sheet with the following headers in the first row:

plaintext
Copy
Edit
vendor | item | model | manufacturer | price | quantity | date
Create a service account in Google Cloud

Share the sheet with the client_email in your service account JSON

Store that credential JSON as service_account.json in your root folder

💡 Tips
Want to support multiple vendors? Include that in your instruction.

Need structured model classification (MCB, MCCB, ACB)? Add it to your prompt.

GPT not extracting all items? Remove character slicing (text[:3500]) and process page-by-page.

🤝 Contributing
Have ideas or want to improve extraction logic? PRs and suggestions welcome!

🛡️ License
MIT License — free to use, modify, and build upon.
