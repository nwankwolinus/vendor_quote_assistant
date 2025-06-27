from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Vendor Quotation Assistant")

app.include_router(router)