import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
from config import OUTPUT_TEXT_FOLDER

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = []

    for page in doc:
        text = page.get_text()

        # If page is scanned (empty text)
        if len(text.strip()) < 20:
            img = page.get_pixmap().pil_tobytes(format="png")
            img = Image.open(io.BytesIO(img))
            text = pytesseract.image_to_string(img)

        full_text.append(text)

    final_text = "\n".join(full_text)

    # Save text file
    file_name = os.path.basename(pdf_path).replace(".pdf", ".txt")
    with open(f"{OUTPUT_TEXT_FOLDER}/{file_name}", "w", encoding="utf-8") as f:
        f.write(final_text)

    return final_text
