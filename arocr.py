import streamlit as st
import pytesseract
import io
import os
import pdfplumber
from pdf2image import convert_from_bytes
from PIL import Image

# Function to check if PDF contains searchable text
def is_searchable_pdf(pdf_bytes):
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text.strip():  # If extracted text is not empty
                return True
    return False

# Function to extract text from each page of a PDF
def extract_text_from_pdf(pdf_bytes):
    full_text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            full_text += f"Page {i + 1}:\n{text}\n\n"
    return full_text

# Function to extract text from an image using OCR
def extract_text_from_image(img_data, lang='ara'):
    if isinstance(img_data, bytes):
        img = Image.open(io.BytesIO(img_data))
    elif isinstance(img_data, Image.Image):
        img = img_data
    else:
        raise ValueError("Input must be either image bytes or a PIL Image object.")

    text = pytesseract.image_to_string(img, lang=lang)
    return text


def main():
    st.title("Arabic OCR with Tesseract")

    # File upload
    uploaded_file = st.file_uploader("Upload PDF or image", type=["pdf", "png", "jpg", "jpeg"])

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()

        if file_ext == "pdf":
            pdf_bytes = uploaded_file.read()
            
            # Check if PDF contains searchable text
            if is_searchable_pdf(pdf_bytes):
                # If searchable text, extract directly
                full_text = extract_text_from_pdf(pdf_bytes)
            else:
                # If scanned images, perform OCR
                images = convert_from_bytes(pdf_bytes)
                full_text = ""
                for i, img in enumerate(images):
                    img_jpeg = img.convert("RGB")
                    text = extract_text_from_image(img_jpeg)
                    full_text += f"Page {i + 1}:\n{text}\n\n"

            st.text_area("Extracted Text", full_text, height=300)

        elif file_ext in ["png", "jpg", "jpeg"]:
            img_bytes = uploaded_file.read()
            text = extract_text_from_image(img_bytes)
            st.text_area("Extracted Text", text, height=300)

        # Remove the uploaded file (PDF or image)
        try:
            os.remove(uploaded_file.name)
        except FileNotFoundError:
            pass  # Ignore FileNotFoundError

if __name__ == "__main__":
    main()
