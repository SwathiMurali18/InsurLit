from fpdf import FPDF
import io
from io import BytesIO
import datetime

def generate_pdf(summary, original_text, readability_score):
    """
    Generate a PDF containing the policy summary and analysis.
    
    Args:
        summary (dict): The structured summary of the policy.
        original_text (str): The original extracted text.
        readability_score (float): The readability score.
        
    Returns:
        bytes: The PDF file as bytes.
    """
    # Create a PDF object with UTF-8 encoding
    pdf = FPDF()
    pdf.add_page()
    
    # Set up the PDF
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ClearInsurance - Policy Summary", ln=True, align="C")
    pdf.line(10, 20, 200, 20)
    pdf.ln(5)
    
    # Add date
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)
    
    # Add readability score
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Readability Analysis", ln=True)
    pdf.set_font("Arial", "", 10)
    
    # Determine difficulty level based on score
    if readability_score <= 50:
        difficulty = "Very Difficult"
    elif readability_score <= 70:
        difficulty = "Moderate"
    else:
        difficulty = "Clear"
    
    pdf.cell(0, 10, f"Readability Score: {readability_score:.1f} - {difficulty}", ln=True)
    pdf.ln(5)
    
    # Add policy summary sections
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Policy Summary", ln=True)
    
    # Add each section of the summary
    if summary:
        sections = [
            ("Coverage Details", summary.get("coverage_details", [])),
            ("Exclusions", summary.get("exclusions", [])),
            ("Deductibles", summary.get("deductibles", [])),
            ("Premiums", summary.get("premiums", [])),
            ("Claims Process", summary.get("claims_process", [])),
            ("Unusual or Hidden Clauses", summary.get("unusual_clauses", []))
        ]
        
        for title, items in sections:
            if items:
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 10, title, ln=True)
                pdf.set_font("Arial", "", 10)
                
                for item in items:
                    # Clean the item of any problematic characters
                    clean_item = item.replace("•", "-")
                    pdf.multi_cell(0, 7, f"- {clean_item}")
                
                pdf.ln(3)
    
    # Add disclaimer
    pdf.ln(5)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Disclaimer: This summary was generated using AI technology and is intended as a guide only. "
                         "It is not a legal interpretation of your insurance policy. "
                         "Always consult with an insurance professional for important decisions.")
    
    # Save the PDF to a bytes object
    pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
    return pdf_bytes
