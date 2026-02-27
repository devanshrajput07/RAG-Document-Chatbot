from PyPDF2 import PdfReader
from docx import Document
import pytesseract
import cv2
import numpy as np
import io

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        try:
            pdf_reader=PdfReader(pdf)
            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
    return text

def get_docx_text(docx_docs):
    text=""
    for doc in docx_docs:
        try:
            doc_reader = Document(doc)
            for para in doc_reader.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading docx format: {e}")
    return text 

def get_txt_text(txt_docs):
    text = ""
    for txt in txt_docs:
        try:
            text += txt.getvalue().decode("utf-8") + "\n"
        except Exception as e:
            print(f"error reading file: {e}")
    return text

import os
# Only set explicit path on Windows. Streamlit Cloud (Linux) finds it automatically.
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  

def extract_text_from_image(image_docs):
    text = ""
    for img_file in image_docs:
        try:
            image_bytes = img_file.read()
            image_np = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            extracted_text = pytesseract.image_to_string(gray)
            if extracted_text.strip():
                text += extracted_text + "\n"
        except Exception as e:
            print(f"Error reading image file: {e}")
    return text

def get_combined_text(uploaded_files):
    pdf_docs = []
    txt_docs = []
    docx_docs = []
    image_docs=[]

    for file in uploaded_files:
        if file.name.endswith(".pdf"):
            pdf_docs.append(file)
        elif file.name.endswith(".txt"):
            txt_docs.append(file)
        elif file.name.endswith(".docx"):
            docx_docs.append(file)
        elif file.name.endswith((".png", ".jpg", ".jpeg")):
            image_docs.append(file)

    raw_text = ""
    if pdf_docs:
        raw_text += get_pdf_text(pdf_docs)
    if txt_docs:
        raw_text += get_txt_text(txt_docs)
    if docx_docs:
        raw_text += get_docx_text(docx_docs)
    if image_docs:
        raw_text+=extract_text_from_image(image_docs)

    return raw_text
