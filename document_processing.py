import os
import io
import tempfile
from PIL import Image
import pytesseract
import pdfplumber
import docx
import streamlit as st

def extract_text_from_pdf(file_content):
    """
    Extract text from PDF files with page numbers and potential section titles.
    
    Returns:
        tuple: (extracted_text, page_info)
            - extracted_text: The full text content
            - page_info: Dictionary mapping page numbers to text content and possible headers
    """
    text = ""
    page_info = {}
    
    with pdfplumber.open(file_content) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text() or ""
            text += page_text + "\n\n"
            
            # Try to identify section headers
            lines = page_text.split('\n')
            headers = []
            
            for line in lines[:5]:  # Check first few lines for potential headers
                # Simple heuristic for headers: short lines with capitalized words or all caps
                if len(line.strip()) < 50 and (any(word.isupper() for word in line.split()) or line.isupper()):
                    headers.append(line.strip())
            
            page_info[i] = {
                "text": page_text,
                "headers": headers
            }
    
    return text, page_info

def extract_text_from_docx(file_content):
    """Extract text from DOCX files."""
    doc = docx.Document(file_content)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_image(file_content):
    """Extract text from image files using OCR."""
    image = Image.open(file_content)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_txt(file_content):
    """Extract text from TXT files."""
    return file_content.read().decode("utf-8")

def extract_text(uploaded_file):
    """
    Extract text from various file formats (PDF, DOCX, images, TXT).
    
    Args:
        uploaded_file: A Streamlit UploadedFile object.
        
    Returns:
        tuple: (extracted_text, document_info)
            - extracted_text: The full text content
            - document_info: Dictionary with metadata about the document (page info for PDFs)
    """
    try:
        file_type = uploaded_file.type
        file_content = io.BytesIO(uploaded_file.getvalue())
        document_info = {"type": file_type, "file_name": uploaded_file.name}
        
        # Based on file type, call the appropriate extraction function
        if file_type == "application/pdf":
            extracted_text, page_info = extract_text_from_pdf(file_content)
            document_info["page_info"] = page_info
            return extracted_text, document_info
        
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extracted_text = extract_text_from_docx(file_content)
            return extracted_text, document_info
        
        elif file_type in ["image/png", "image/jpeg", "image/jpg"]:
            extracted_text = extract_text_from_image(file_content)
            return extracted_text, document_info
        
        elif file_type == "text/plain":
            extracted_text = extract_text_from_txt(file_content)
            return extracted_text, document_info
        
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        raise e
