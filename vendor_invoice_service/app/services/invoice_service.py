from PIL import Image
import pytesseract
from app.core.config import db
from app.models.invoice import Invoice, InvoiceItem

# Hugging Face imports
from transformers import AutoProcessor, AutoModelForTokenClassification
import torch

# Initialize Hugging Face model
processor = AutoProcessor.from_pretrained("Theivaprakasham/layoutlmv3-finetuned-invoice")
model = AutoModelForTokenClassification.from_pretrained("Theivaprakasham/layoutlmv3-finetuned-invoice")

def extract_text_from_image(image_file) -> Image.Image:
    """Load image from UploadFile and return PIL Image."""
    return Image.open(image_file)

def parse_invoice_with_hf(image: Image.Image) -> Invoice:
    """
    Use LayoutLMv3 to extract structured data from invoice.
    """
    try:
        # Extract OCR data using pytesseract
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # Filter out empty text and create words list
        words = []
        boxes = []
        for i, text in enumerate(ocr_data['text']):
            if text.strip():
                words.append(text)
                # LayoutLMv3 expects bounding boxes in [x0, y0, x1, y1] format
                x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                boxes.append([x, y, x + w, y + h])
        
        # Handle case where no text is detected
        if not words:
            return Invoice(
                supplier_name="Unknown Supplier",
                total_amount=0.0,
                items=[],
                status="pending"
            )
        
        # Prepare inputs for LayoutLMv3 processor
        encoding = processor(
            image,
            words,
            boxes=boxes,
            return_tensors="pt",
            padding="max_length",
            truncation=True
        )
        
        outputs = model(**encoding)
        
        # Get predicted tokens
        logits = outputs.logits
        predicted_ids = torch.argmax(logits, dim=2)
        tokens = processor.tokenizer.convert_ids_to_tokens(encoding["input_ids"][0])
        labels = [model.config.id2label[id.item()] for id in predicted_ids[0]]

        # Simple post-processing: extract fields
        supplier_name = "Unknown Supplier"
        total_amount = 0.0
        items = []

        current_item = {}
        for token, label in zip(tokens, labels):
            if label == "B-SUPPLIER" or label == "I-SUPPLIER":
                supplier_name += f" {token}".replace("##", "")
            elif label == "B-TOTAL" or label == "I-TOTAL":
                try:
                    total_amount = float(token.replace("$", "").replace(",", "").strip())
                except:
                    continue
            elif label.startswith("B-ITEM") or label.startswith("I-ITEM"):
                # Aggregate item info
                if "description" not in current_item:
                    current_item["description"] = token
                else:
                    current_item["description"] += f" {token}".replace("##", "")
            elif label.startswith("B-PRICE") or label.startswith("I-PRICE"):
                try:
                    current_item["price"] = float(token.replace("$", "").replace(",", ""))
                except:
                    current_item["price"] = 0.0
            elif label.startswith("B-QUANTITY") or label.startswith("I-QUANTITY"):
                try:
                    current_item["quantity"] = int(token)
                except:
                    current_item["quantity"] = 1
            
            # End of item
            if label == "O" and current_item:
                items.append(InvoiceItem(**current_item))
                current_item = {}

        return Invoice(
            supplier_name=supplier_name.strip(),
            total_amount=total_amount,
            items=items,
            status="pending"
        )
        
    except Exception as e:
        # Fallback to basic OCR-based extraction if LayoutLMv3 fails
        print(f"Error in LayoutLMv3 processing: {e}")
        
        # Basic fallback using just OCR text
        text = pytesseract.image_to_string(image)
        
        # Simple regex-based extraction as fallback
        import re
        
        # Try to extract supplier name (first line of text)
        lines = text.strip().split('\n')
        supplier_name = lines[0] if lines else "Unknown Supplier"
        
        # Try to extract total amount
        total_match = re.search(r'(?:TOTAL|Total|total)[\s:]*\$?(\d+\.?\d*)', text)
        total_amount = float(total_match.group(1)) if total_match else 0.0
        
        # Create basic invoice structure
        return Invoice(
            supplier_name=supplier_name,
            total_amount=total_amount,
            items=[],  # Could add basic item extraction here
            status="pending"
        )

def save_invoice_to_firestore(invoice: Invoice):
    """
    Saves parsed invoice into Firestore.
    """
    doc_ref = db.collection("invoices").document()
    doc_ref.set(invoice.dict())
    return doc_ref.id


# import os
# from huggingface_hub import InferenceClient

# # In production, store this in .env
# HF_API_TOKEN = os.getenv("HF_API_TOKEN", "your_huggingface_token")
# MODEL_ID = "distilbert-base-uncased"  # placeholder, replace with invoice model

# client = InferenceClient(model=MODEL_ID, token=HF_API_TOKEN)

# async def parse_invoice(file):
#     """
#     Core AI Integration Point: This function calls Hugging Face
#     to extract structured invoice data.
#     """
#     # Read file content
#     content = await file.read()
#     text = content.decode("utf-8", errors="ignore")  # simple text extraction for now

#     # Call Hugging Face API (example: text classification)
#     response = client.text_classification(text)
    
#     return response
