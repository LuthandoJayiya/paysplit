from fastapi import APIRouter, UploadFile, File
from app.services.invoice_service import extract_text_from_image, parse_invoice_with_hf, save_invoice_to_firestore

router = APIRouter()

@router.post("/invoice/upload")
async def upload_invoice(file: UploadFile = File(...)):
    """
    Upload invoice (image/pdf), parse with Hugging Face LayoutLMv3,
    and save to Firestore.
    """
    # 1. Extract image
    image = extract_text_from_image(file.file)

    # 2. Parse invoice using HF model
    invoice = parse_invoice_with_hf(image)

    # 3. Save to Firestore
    invoice_id = save_invoice_to_firestore(invoice)

    return {
        "message": "Invoice uploaded successfully",
        "invoice_id": invoice_id,
        "parsed_data": invoice.dict()
    }
