import streamlit as st
import anthropic
import os
import io
from PIL import Image
from pdf2image import convert_from_bytes
import pdfplumber
import pytesseract
import pyperclip  # Import the pyperclip library

# Function to authenticate users
def authenticate(username, password):
    valid_usernames = st.secrets["valid_usernames"]
    valid_passwords = st.secrets["valid_passwords"]

    if username in valid_usernames and password == valid_passwords[valid_usernames.index(username)]:
        return True
    else:
        return False

# Function to display login form
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password. Please try again.")

# Function to display authenticated content
def main():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login()
    else:
        st.title("Authenticated Content")

# Set up the Anthropic API client
anthropic_api_key = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=anthropic_api_key)

# Function to check if PDF contains searchable text
def is_searchable_pdf(pdf_bytes):
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text.strip():
                return True
    return False

# Function to extract text from each page of a PDF
def extract_text_from_pdf(pdf_bytes, lang='fra'):
    full_text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            full_text += f"Page {i + 1}:\n{text}\n\n"
    return full_text

# Function to extract text from an image using OCR
def extract_text_from_image(img_data, lang='fra'):
    if isinstance(img_data, bytes):
        img = Image.open(io.BytesIO(img_data))
    elif isinstance(img_data, Image.Image):
        img = img_data
    else:
        raise ValueError("Input must be either image bytes or a PIL Image object.")
    text = pytesseract.image_to_string(img, lang=lang)
    return text

def main():
    st.title("Ai Fusion SolidBrain1")

    # Add a sidebar section for file upload and language selection
    with st.sidebar:
        st.title("Arabic or French Text Extraction")
        language = st.radio("Select Language", options=["Arabic", "French"])
        uploaded_file = st.file_uploader("Upload PDF or image", type=["pdf", "png", "jpg", "jpeg"])

    # Initialize chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    user_input = st.chat_input("Type your message here")
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Generate response from Anthropic Claude
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0.1,  # Set the temperature here
            system="You are a helpful, friendly, and informative assistant.",  # Set the system message here
            messages=st.session_state.chat_history,
        )
        assistant_response = "".join(block.text for block in response.content)

        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Display the assistant's response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    # Process the uploaded file
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()

        if language == "Arabic":
            if file_ext == "pdf":
                pdf_bytes = uploaded_file.read()
                if is_searchable_pdf(pdf_bytes):
                    full_text = extract_text_from_pdf(pdf_bytes, lang='ara')
                else:
                    images = convert_from_bytes(pdf_bytes)
                    full_text = ""
                    for i, img in enumerate(images):
                        img_jpeg = img.convert("RGB")
                        text = extract_text_from_image(img_jpeg, lang='ara')
                        full_text += f"Page {i + 1}:\n{text}\n\n"
            elif file_ext in ["png", "jpg", "jpeg"]:
                img_bytes = uploaded_file.read()
                full_text = extract_text_from_image(img_bytes, lang='ara')

        elif language == "French":
            if file_ext == "pdf":
                pdf_bytes = uploaded_file.read()
                if is_searchable_pdf(pdf_bytes):
                    full_text = extract_text_from_pdf(pdf_bytes, lang='fra')
                else:
                    images = convert_from_bytes(pdf_bytes)
                    full_text = ""
                    for i, img in enumerate(images):
                        img_jpeg = img.convert("RGB")
                        text = extract_text_from_image(img_jpeg, lang='fra')
                        full_text += f"Page {i + 1}:\n{text}\n\n"
            elif file_ext in ["png", "jpg", "jpeg"]:
                img_bytes = uploaded_file.read()
                full_text = extract_text_from_image(img_bytes, lang='fra')

        # Display the extracted text and add a copy button
        with st.sidebar.expander("Extracted Text"):
            st.text_area("", full_text, height=300)
            if st.button("Copy Text"):
                pyperclip.copy(full_text)
                st.success("Text copied to clipboard!")

        # Remove the uploaded file
        try:
            os.remove(uploaded_file.name)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    main()

