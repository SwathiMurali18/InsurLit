import os
import json
import google.generativeai as genai
import streamlit as st

# Configure the Gemini API with the API key
API_KEY = os.getenv("GEMINI_API_KEY")

def setup_gemini():
    """Configure the Gemini API with the provided API key."""
    if not API_KEY:
        st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
        return False
    
    genai.configure(api_key=API_KEY)
    return True

def generate_summary(text, document_info=None, readability_preference="Easy (Elementary School Level)"):
    """
    Generate a structured summary of the insurance policy using Gemini API.
    
    Args:
        text (str): The extracted text from the insurance document.
        document_info (dict, optional): Document metadata containing page numbers and section headers.
        readability_preference (str, optional): The level of readability to target ("Easy" or "Moderate").
        
    Returns:
        dict: A dictionary containing structured summaries for each section.
    """
    if not setup_gemini():
        return {
            "coverage_details": ["API key not configured. Unable to generate summary."],
            "exclusions": [],
            "deductibles": [],
            "premiums": [],
            "claims_process": [],
            "unusual_clauses": []
        }
    
    try:
        # First, verify if this is actually an auto insurance document
        verification_prompt = f"""
        You are an insurance policy expert. Review the following document text and determine if it is an auto insurance policy.

        Document text:
        {text[:1500]}  # Using first 1500 chars to save tokens

        Is this document an auto insurance policy? 
        Respond with only "yes" if it is an auto insurance policy document.
        Respond with "no: [document type]" if it is not, where [document type] is a brief description of what the document actually is.
        """
        
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        verification_response = model.generate_content(verification_prompt)
        verification_result = verification_response.text.strip().lower()
        
        # If not an auto insurance document, return error
        if not verification_result.startswith("yes"):
            document_type = verification_result.replace("no:", "").strip() if ":" in verification_result else "not an auto insurance policy"
            return {
                "coverage_details": [f"This document appears to be {document_type}. Please upload an auto insurance policy document."],
                "exclusions": [],
                "deductibles": [],
                "premiums": [],
                "claims_process": [],
                "unusual_clauses": []
            }
        
        # Prepare document reference information for the prompt
        reference_info = ""
        if document_info and document_info.get("type") == "application/pdf" and "page_info" in document_info:
            reference_info = "Page and section information:\n"
            for page_num, info in document_info["page_info"].items():
                headers = info.get("headers", [])
                if headers:
                    reference_info += f"Page {page_num}: {', '.join(headers)}\n"
                else:
                    reference_info += f"Page {page_num}\n"
        
        # Set readability target based on preference
        readability_target = ""
        if readability_preference == "Easy (Elementary School Level)":
            readability_target = """
            VERY IMPORTANT: Your summary MUST be written at an elementary school reading level (Flesch-Kincaid score between 71-100). 
            Use very short sentences (10-15 words), simple words (1-2 syllables), and basic everyday vocabulary.
            Completely avoid complex terms, technical jargon, and legal language.
            """
        else:  # Moderate (High School Level)
            readability_target = """
            VERY IMPORTANT: Your summary MUST be written at a high school reading level (Flesch-Kincaid score between 51-70). 
            Use moderate-length sentences (15-20 words), simple to moderate vocabulary, and clear explanations.
            Minimize complex terms, technical jargon, and legal language, but you can include more detail than in an elementary-level summary.
            """
        
        # Determine audience based on preference
        audience = "elementary school student" if readability_preference == "Easy (Elementary School Level)" else "high school student"
            
        # Create a prompt for the Gemini API
        prompt = f"""
        You are an insurance policy expert. Analyze the following auto insurance policy text and provide a clear, 
        structured summary in plain language that a typical {audience} can understand. 
        
        Policy text:
        {text}
        
        {reference_info}
        
        Please format your response as a JSON object with the following sections:
        1. coverage_details: List of what is covered in plain language.
        2. exclusions: List of what is not covered.
        3. deductibles: List explaining deductible amounts and when they apply.
        4. premiums: List explaining the premium structure and payment details.
        5. claims_process: List summarizing how to file a claim and what to expect.
        6. unusual_clauses: List identifying any unusual or potentially hidden clauses that consumers should be aware of.
        
        Each section should contain an array of strings, with each string being a clear, simple bullet point.
        When possible, include the page number or section reference where this information is found (e.g., "Coverage for rentals is included (Page 3, RENTAL COVERAGE section)").
        
        {readability_target}
        
        If information for a section is not found, provide an empty array.
        Ensure your response is valid JSON that can be parsed by Python's json.loads().
        """
        
        # Generate the content with Gemini
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        # Parse the response as JSON
        response_text = response.text
        
        # Check if the response is wrapped in triple backticks and a JSON indicator
        if "```json" in response_text and "```" in response_text:
            json_content = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_content = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_content = response_text
        
        # Clean the JSON content to handle potential escape character issues
        json_content = json_content.replace('\\', '\\\\')
        
        try:
            summary = json.loads(json_content)
        except json.JSONDecodeError:
            # If we can't parse as JSON, create a simple structure with the error text
            st.warning("Could not parse model response as JSON. Creating simplified summary.")
            summary = {
                "coverage_details": ["Could not generate detailed summary. Please try uploading the document again."],
                "exclusions": [],
                "deductibles": [],
                "premiums": [],
                "claims_process": [],
                "unusual_clauses": []
            }
        
        # Ensure all expected keys are present
        expected_keys = [
            "coverage_details", "exclusions", "deductibles", 
            "premiums", "claims_process", "unusual_clauses"
        ]
        
        for key in expected_keys:
            if key not in summary:
                summary[key] = []
        
        return summary
    
    except Exception as e:
        st.error(f"Error generating summary with Gemini API: {str(e)}")
        return {
            "coverage_details": [f"Error generating summary: {str(e)}"],
            "exclusions": [],
            "deductibles": [],
            "premiums": [],
            "claims_process": [],
            "unusual_clauses": []
        }

def answer_question(question, document_text, document_info=None, readability_preference="Easy (Elementary School Level)"):
    """
    Use Gemini API to answer a specific question about the insurance policy.
    
    Args:
        question (str): The user's question about the policy.
        document_text (str): The extracted text from the insurance document.
        document_info (dict, optional): Document metadata containing page numbers and section headers.
        readability_preference (str, optional): The level of readability to target ("Easy" or "Moderate").
        
    Returns:
        str: The answer to the user's question.
    """
    if not setup_gemini():
        return "API key not configured. Unable to answer questions."
    
    try:
        # First, verify if this is actually an auto insurance document
        verification_prompt = f"""
        You are an insurance policy expert. Review the following document text and determine if it is an auto insurance policy.

        Document text:
        {document_text[:1500]}  # Using first 1500 chars to save tokens

        Is this document an auto insurance policy? 
        Respond with only "yes" if it is an auto insurance policy document.
        Respond with "no: [document type]" if it is not, where [document type] is a brief description of what the document actually is.
        """
        
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        verification_response = model.generate_content(verification_prompt)
        verification_result = verification_response.text.strip().lower()
        
        # If not an auto insurance document, return error
        if not verification_result.startswith("yes"):
            document_type = verification_result.replace("no:", "").strip() if ":" in verification_result else "not an auto insurance policy"
            return f"I cannot answer your question because this document appears to be {document_type}. Please upload an auto insurance policy document."
        
        # Prepare document reference information for the prompt
        reference_info = ""
        if document_info and document_info.get("type") == "application/pdf" and "page_info" in document_info:
            reference_info = "Page and section information:\n"
            for page_num, info in document_info["page_info"].items():
                headers = info.get("headers", [])
                if headers:
                    reference_info += f"Page {page_num}: {', '.join(headers)}\n"
                else:
                    reference_info += f"Page {page_num}\n"
        
        # Set readability target based on preference
        readability_target = ""
        if readability_preference == "Easy (Elementary School Level)":
            readability_target = """
            VERY IMPORTANT: Your answer MUST be written at an elementary school reading level (Flesch-Kincaid score between 71-100). 
            Use very short sentences (10-15 words), simple words (1-2 syllables), and basic everyday vocabulary.
            Completely avoid complex terms, technical jargon, and legal language.
            """
        else:  # Moderate (High School Level)
            readability_target = """
            VERY IMPORTANT: Your answer MUST be written at a high school reading level (Flesch-Kincaid score between 51-70). 
            Use moderate-length sentences (15-20 words), simple to moderate vocabulary, and clear explanations.
            Minimize complex terms, technical jargon, and legal language, but you can include more detail than in an elementary-level answer.
            """
            
        # Create a prompt for the Gemini API
        prompt = f"""
        You are an insurance policy expert. Answer the following question about an auto insurance policy 
        based on the policy text provided. When possible, cite specific page numbers and sections from the policy.
        
        Policy text:
        {document_text}
        
        {reference_info}
        
        Question: {question}
        
        Provide a clear, accurate answer based solely on the content of the policy. If the information is not 
        found in the policy, state that clearly. Format your response in plain language that's easy to understand.
        When relevant, include page numbers and section references in your answer (e.g., "According to Page 3, RENTAL COVERAGE section, your policy covers...").
        
        {readability_target}
        """
        
        # Generate the content with Gemini
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        st.error(f"Error answering question with Gemini API: {str(e)}")
        return f"Sorry, I couldn't process your question due to an error: {str(e)}"
