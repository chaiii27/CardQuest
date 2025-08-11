# Overview

AI Flashcard Generator is a Streamlit-based web application that leverages Google's Gemini AI model to automatically generate study flashcards from PDF documents. The application extracts text content from uploaded PDFs and creates intelligent question-answer pairs for educational purposes, with features for interactive studying and CSV export functionality.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web framework for rapid prototyping and deployment
- **Layout**: Wide layout configuration with responsive design
- **User Interface**: Clean, interactive interface with file upload, flashcard navigation, and export capabilities
- **Session Management**: Streamlit's built-in session state for maintaining user data across interactions

## Backend Architecture
- **Processing Pipeline**: Sequential workflow from PDF upload → text extraction → AI generation → flashcard display
- **Text Extraction**: PyPDF2 library for parsing PDF documents and extracting readable text content
- **AI Integration**: Google Gemini AI model for intelligent flashcard generation from extracted text
- **Data Handling**: In-memory processing with pandas DataFrames for flashcard management

## Configuration Management
- **API Key Management**: Flexible configuration supporting both Streamlit secrets and environment variables
- **Error Handling**: Comprehensive error checking for missing API keys and processing failures
- **Environment Setup**: Simple pip-based dependency management

## Data Flow
1. User uploads PDF file through Streamlit file uploader
2. PyPDF2 extracts text content from all pages
3. Google Gemini processes text and generates question-answer pairs
4. Flashcards are displayed in interactive study mode
5. Users can export results as CSV for offline use

# External Dependencies

## AI Services
- **Google Gemini API**: Gemini-2.5-flash model for natural language processing and flashcard generation
- **Authentication**: API key-based authentication with Google Gemini services

## File Processing
- **PyPDF2**: Python library for PDF text extraction and document parsing
- **Pandas**: Data manipulation and CSV export functionality

## Web Framework
- **Streamlit**: Complete web application framework with built-in hosting capabilities
- **Standard Libraries**: io, json, os for file handling and data processing

## Deployment Requirements
- **Environment Variables**: GEMINI_API_KEY for API authentication
- **Python Dependencies**: All requirements managed through requirements.txt file