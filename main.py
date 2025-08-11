import streamlit as st
import PyPDF2
import pandas as pd
import json
import os
import io
from google import genai
from google.genai import types

# Page configuration
st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="icon.png",
    layout="wide"
)

def get_gemini_client():
    """Initialize Gemini client with API key from environment or secrets."""
    try:
        # First try environment variable (Replit Secrets)
        api_key = os.getenv('GEMINI_API_KEY')
        
        # Then try Streamlit secrets as fallback
        if not api_key:
            try:
                if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                    api_key = st.secrets['GEMINI_API_KEY']
            except Exception:
                pass  # Streamlit secrets not available
        
        if not api_key:
            st.error("Gemini API key not found. Please ensure GEMINI_API_KEY is set in your environment variables.")
            st.info("The API key should be available as an environment variable from Replit Secrets.")
            st.stop()
        
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Gemini client: {str(e)}")
        st.stop()

def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        total_pages = len(pdf_reader.pages)
        
        st.info(f"Processing {total_pages} pages...")
        
        for page_num in range(total_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            text += page_text + "\n"
            
            # Show progress for larger documents
            if total_pages > 5 and page_num % 5 == 0:
                st.info(f"Processed page {page_num + 1} of {total_pages}")
        
        final_text = text.strip()
        if not final_text:
            st.warning("PDF processed but no text found. This might be an image-based PDF.")
        
        return final_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        st.error("Please try a different PDF file or check if the file is corrupted.")
        return None

def generate_flashcards(text, num_cards=10):
    """Generate flashcards from text using Gemini API."""
    client = get_gemini_client()
    
    try:
        # Note that the newest Gemini model series is "gemini-2.5-flash" or "gemini-2.5-pro"
        # do not change this unless explicitly requested by the user
        system_prompt = f"""You are an expert educator who creates high-quality study flashcards. 
        Based on the following text, create {num_cards} educational flashcards for studying.
        Each flashcard should have a clear question and a comprehensive answer.
        Focus on key concepts, important facts, definitions, and relationships.
        
        Return the response as a JSON object with this exact format:
        {{"flashcards": [{{"question": "Question text here", "answer": "Answer text here"}}]}}"""
        
        user_content = f"Text to analyze:\n{text[:4000]}"  # Limit text to avoid token limits
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_content)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            ),
        )
        
        content = response.text
        if not content:
            st.error("No content received from Gemini API")
            return []
        
        result = json.loads(content)
        return result.get("flashcards", [])
        
    except Exception as e:
        st.error(f"Error generating flashcards: {str(e)}")
        return []

def display_flashcards(flashcards):
    """Display flashcards in an interactive format."""
    if not flashcards:
        st.warning("No flashcards generated.")
        return
    
    st.subheader(f"Generated {len(flashcards)} Flashcards")
    
    # Initialize session state for flashcard navigation
    if 'current_card' not in st.session_state:
        st.session_state.current_card = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    
    # Navigation controls with better alignment
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_card == 0):
            st.session_state.current_card -= 1
            st.session_state.show_answer = False
            st.rerun()
    
    with col2:
        # Custom Next button with icon
        if st.button("➡️ Next", disabled=st.session_state.current_card >= len(flashcards) - 1):
            st.session_state.current_card += 1
            st.session_state.show_answer = False
            st.rerun()
    
    with col3:
        st.markdown(
            f"<div style='text-align: center; padding: 10px;'><strong>Card {st.session_state.current_card + 1} of {len(flashcards)}</strong></div>",
            unsafe_allow_html=True
        )
    
    with col4:
        # Custom Show/Hide button with icon
        if st.button("💡 Show/Hide Answer"):
            st.session_state.show_answer = not st.session_state.show_answer
            st.rerun()
    
    with col5:
        # Custom Random button with icon
        if st.button("🔀 Random Card"):
            import random
            st.session_state.current_card = random.randint(0, len(flashcards) - 1)
            st.session_state.show_answer = False
            st.rerun()
    
    # Display current flashcard
    current_flashcard = flashcards[st.session_state.current_card]
    
    # Question card
    st.markdown("### 🤔 Question")
    question_container = st.container()
    with question_container:
        st.markdown(f"**{current_flashcard['question']}**")
    
    # Answer card (conditional display)
    if st.session_state.show_answer:
        st.markdown("### 💡 Answer")
        answer_container = st.container()
        with answer_container:
            st.markdown(current_flashcard['answer'])
    else:
        st.info("Click 'Show/Hide Answer' to reveal the answer")

def create_csv_download(flashcards):
    """Create CSV download functionality for flashcards."""
    if not flashcards:
        return None
    
    # Convert flashcards to DataFrame
    df = pd.DataFrame(flashcards)
    
    # Create CSV buffer
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    return csv_data

def main():
    """Main application function."""
    st.title("🧠 AI Flashcard Generator")
    st.markdown("Upload a PDF document and generate AI-powered flashcards for studying!")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Settings")
        num_cards = st.slider("Number of flashcards to generate", min_value=5, max_value=25, value=10)
        
        st.markdown("---")
        st.markdown("### 📚 How to use:")
        st.markdown("1. Upload a PDF file")
        st.markdown("2. Wait for text extraction")
        st.markdown("3. Generate flashcards with AI")
        st.markdown("4. Study and download CSV")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to extract content and generate flashcards"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"File size: {len(uploaded_file.getvalue())} bytes")
        
        # Extract text from PDF
        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
        
        if extracted_text and len(extracted_text.strip()) > 0:
            st.success("Text extracted successfully!")
            st.info(f"Extracted {len(extracted_text)} characters of text")
            
            # Show text preview
            with st.expander("📄 Preview extracted text (first 500 characters)"):
                st.text(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
            
            # Generate flashcards button
            if st.button("🚀 Generate Flashcards", type="primary"):
                with st.spinner(f"Generating {num_cards} flashcards using AI..."):
                    flashcards = generate_flashcards(extracted_text, num_cards)
                
                if flashcards:
                    # Store flashcards in session state
                    st.session_state.flashcards = flashcards
                    st.session_state.current_card = 0
                    st.session_state.show_answer = False
                    st.success(f"Successfully generated {len(flashcards)} flashcards!")
                else:
                    st.error("Failed to generate flashcards. Please try again.")
        else:
            st.error("No text could be extracted from the PDF. The file might be image-based, corrupted, or empty. Please try a different PDF file.")
    
    # Display flashcards if they exist in session state
    if 'flashcards' in st.session_state and st.session_state.flashcards:
        st.markdown("---")
        display_flashcards(st.session_state.flashcards)
        
        # CSV download section
        st.markdown("---")
        st.subheader("📥 Export Flashcards")
        
        csv_data = create_csv_download(st.session_state.flashcards)
        if csv_data:
            st.download_button(
                label="📄 Download as CSV",
                data=csv_data,
                file_name="flashcards.csv",
                mime="text/csv",
                help="Download all flashcards as a CSV file for offline studying"
            )
        
        # Clear flashcards button
        if st.button("🗑️ Clear Flashcards"):
            del st.session_state.flashcards
            if 'current_card' in st.session_state:
                del st.session_state.current_card
            if 'show_answer' in st.session_state:
                del st.session_state.show_answer
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>AI Flashcard Generator - Powered by Google Gemini - Made by Chaimaa Ramlaouane</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
