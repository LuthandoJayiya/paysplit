from fastapi import FastAPI
from app.api.v1.endpoints import invoice_routes

app = FastAPI(title="Invoice Service")

# Register routers
app.include_router(invoice_routes.router, tags=["Invoices"])

@app.get("/")
def health_check():
    return {"status": "Invoice Service running"}
