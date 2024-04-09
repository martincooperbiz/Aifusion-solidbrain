import streamlit as st
import requests
import io
import os
import fitz  # PyMuPDF
from pdf2image import convert_from_bytes
from PIL import Image

# Function to check if PDF contains searchable text
def is_searchable_pdf(pdf_bytes):
    # Use PyMuPDF to check if the PDF contains text
    pdf_document = fitz.open(stream=io.BytesIO(pdf_bytes))
    for page in pdf_document:
        if page.get_text():
            return True
    return False

# Function to extract text from each page of a PDF using PyMuPDF
def extract_text_from_pdf(pdf_bytes):
    pdf_document = fitz.open(stream=io.BytesIO(pdf_bytes))
    full_text = ""
    for page in pdf_document:
        full_text += page.get_text()
    return full_text

# Function to extract text from an image using OCR.space API
def extract_text_from_image(img_data, lang='ara'):
    # Function remains unchanged
    pass

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
            img = Image.open(io.BytesIO(img_bytes))
            text = extract_text_from_image(img)
            st.text_area("Extracted Text", text, height=300)

        # Remove the uploaded file (PDF or image)
        try:
            os.remove(uploaded_file.name)
        except FileNotFoundError:
            pass  # Ignore FileNotFoundError

if __name__ == "__main__":
    main()
