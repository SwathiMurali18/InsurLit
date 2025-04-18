import streamlit as st
import document_processing as dp
import gemini_integration as gi
import readability as rd
import pdf_export as pe
import base64


# Load environment variables from .env file


# App header
st.title("InsurLit – Understand Your Policy, Clearly")
st.write("Upload your auto insurance document to get a clear, plain-language summary and analysis.")

# Initialize session state variables if they don't exist
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'document_info' not in st.session_state:
    st.session_state.document_info = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'readability_score' not in st.session_state:
    st.session_state.readability_score = None
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []
if 'readability_preference' not in st.session_state:
    st.session_state.readability_preference = "Easy (Elementary School Level)"

# Sidebar - File upload and FAQs
with st.sidebar:
    st.header("Upload Document")
    st.write("Supported formats: PDF, DOCX, PNG, JPG, TXT")
    
    # Add readability preference dropdown
    readability_preference = st.selectbox(
        "Choose summary language level:",
        options=["Easy (Elementary School Level)", "Moderate (High School Level)"],
        index=0,  # Default to Easy
        help="Select how simple you want the language in your summary to be"
    )
    # Save the preference to session state
    st.session_state.readability_preference = readability_preference
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
        help="Upload your insurance policy document"
    )
    
    if uploaded_file is not None:
        # Process the uploaded file
        try:
            # Reset previous data when a new document is uploaded
            st.session_state.qa_history = []
            
            with st.spinner("Extracting text from document..."):
                extracted_text, document_info = dp.extract_text(uploaded_file)
                st.session_state.extracted_text = extracted_text
                st.session_state.document_info = document_info
                
                # Calculate readability score
                st.session_state.readability_score = rd.calculate_readability_score(extracted_text)
                
                # Generate summary with Gemini API
                with st.spinner("Analyzing your policy with AI..."):
                    st.session_state.summary = gi.generate_summary(
                        extracted_text, 
                        document_info,
                        st.session_state.readability_preference
                    )
                
                st.success("Document processed successfully!")
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
    
    st.header("FAQs")
    with st.expander("How does InsurLit work?"):
        st.write("InsurLit uses AI to read and simplify your insurance documents. Upload your policy, and we'll extract the text, analyze it, and provide a plain-language summary with important highlights.")
    
    with st.expander("Is my data secure?"):
        st.write("We process your documents locally. Your data or the document is not stored on our servers and is used only for the current session.")
    
    with st.expander("How accurate is the AI analysis?"):
        st.write("While our AI system provides high-quality summaries, it's designed to be a helpful guide, not legal advice. Always consult with an insurance professional for critical decisions.")

# Main content
if st.session_state.extracted_text:
    # Always display in Simple View mode
    if st.session_state.summary:
        st.header("Policy Summary")
        
        # Display coverage details
        if st.session_state.summary.get("coverage_details"):
            st.subheader("Coverage Details")
            for item in st.session_state.summary["coverage_details"]:
                st.markdown(f"• {item}")
        
        # Display exclusions
        if st.session_state.summary.get("exclusions"):
            st.subheader("Exclusions")
            for item in st.session_state.summary["exclusions"]:
                st.markdown(f"• {item}")
        
        # Display deductibles
        if st.session_state.summary.get("deductibles"):
            st.subheader("Deductibles")
            for item in st.session_state.summary["deductibles"]:
                st.markdown(f"• {item}")
        
        # Display premiums
        if st.session_state.summary.get("premiums"):
            st.subheader("Premiums")
            for item in st.session_state.summary["premiums"]:
                st.markdown(f"• {item}")
        
        # Display claims process
        if st.session_state.summary.get("claims_process"):
            st.subheader("Claims Process")
            for item in st.session_state.summary["claims_process"]:
                st.markdown(f"• {item}")
        
        # Display unusual/hidden clauses
        if st.session_state.summary.get("unusual_clauses"):
            st.subheader("Unusual or Hidden Clauses")
            for item in st.session_state.summary["unusual_clauses"]:
                st.markdown(f"• {item}", unsafe_allow_html=True)
    
    # Removed original text section as requested
    
    # Readability analysis
    if st.session_state.readability_score is not None and st.session_state.summary:
        st.header("Policy Readability")
        
        # Original document score
        original_score = st.session_state.readability_score
        # Determine color based on score
        if original_score <= 50:
            original_color = "red"
            original_difficulty = "Very Hard to Read"
        elif original_score <= 70:
            original_color = "orange"
            original_difficulty = "Moderate"
        else:
            original_color = "green"
            original_difficulty = "Clear"
        
        st.subheader("Original Document")
        st.write(f"Readability Score: **{original_score:.1f}** - *{original_difficulty}*")
        st.progress(original_score/100)
        
        # Summary score
        # Join all summary items into one text
        summary_text = ""
        for section, items in st.session_state.summary.items():
            summary_text += ' '.join(items) + " "
        
        summary_score = rd.calculate_readability_score(summary_text)
        # Determine color based on score
        if summary_score <= 50:
            summary_color = "red"
            summary_difficulty = "Very Hard to Read"
        elif summary_score <= 70:
            summary_color = "orange"
            summary_difficulty = "Moderate"
        else:
            summary_color = "green"
            summary_difficulty = "Clear"
        
        st.subheader("AI-Generated Summary")
        st.write(f"Readability Score: **{summary_score:.1f}** - *{summary_difficulty}*")
        st.progress(summary_score/100)
        
        # Explanation of the score
        with st.expander("What do these scores mean?"):
            st.write("""
            The Flesch-Kincaid readability score measures how easy a text is to understand:
            - 0-50: Very difficult, typically requires college-level education
            - 51-70: Moderately difficult, readable by high school students
            - 71-100: Easy to read, understandable by most 12-year-olds
            
            Most insurance policies score between 30-50, making them challenging for the average person to understand.
            Our AI-generated summary aims to improve readability significantly.
            """)
    
    # Interactive Q&A with conversation history
    st.header("Ask about your policy")
    user_question = st.text_input("Ask a question about your policy (e.g., 'Am I covered for rental cars?')")
    
    # Current answer first
    if user_question and st.session_state.extracted_text:
        with st.spinner("Generating answer..."):
            answer = gi.answer_question(
                question=user_question, 
                document_text=st.session_state.extracted_text,
                document_info=st.session_state.document_info,
                readability_preference=st.session_state.readability_preference
            )
            
            # Add to conversation history
            st.session_state.qa_history.append((user_question, answer))
            
            # Display the current answer
            st.subheader("Current Answer")
            st.write(answer)
            
            # Display previous Q&A below but only when there are at least 2 questions
            if len(st.session_state.qa_history) > 1:
                st.subheader("Previous Questions & Answers")
                # We're showing all question-answer pairs, most recent first (excluding the current one)
                for q, a in reversed(st.session_state.qa_history[:-1]):
                    with st.expander(f"Q: {q}", expanded=False):
                        st.markdown(f"**Answer:** {a}")
    # If no current question but we have history, show all history
    elif len(st.session_state.qa_history) > 0:
        st.subheader("Previous Questions & Answers")
        for q, a in reversed(st.session_state.qa_history):
            with st.expander(f"Q: {q}", expanded=False):
                st.markdown(f"**Answer:** {a}")
    
    # Export options
    st.header("Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download as PDF", use_container_width=True):
            try:
                with st.spinner("Generating PDF..."):
                    pdf_bytes = pe.generate_pdf(
                        st.session_state.summary,
                        st.session_state.extracted_text,
                        st.session_state.readability_score
                    )
                    
                    # Create a download link
                    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="InsurLit_Summary.pdf">Click to download your PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        email = st.text_input("Email address", placeholder="Enter your email")
        if st.button("Send to Email", use_container_width=True) and email:
            # This is a placeholder for actual email functionality
            st.info("Email functionality is a placeholder. In a production environment, this would send the PDF to your email.")

# Footer - Trust elements
st.markdown("---")
st.caption("""
**Disclaimer**: This application uses AI to analyze and summarize insurance documents. While we strive for accuracy, 
the information provided should not be considered legal advice. Always consult with an insurance professional 
when making decisions based on your policy.

**Privacy**: Your documents are processed only during your current session. Your data or the document is not stored on our servers and is used only for the current session. No personally identifiable information is collected or retained.
""")
