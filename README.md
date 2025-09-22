# Personal LMS (Flask + LangGraph + Gemini AI)

This project implements a Personal Learning Management System (PLMS) chatbot using **Flask**, **LangGraph**, and **Google Gemini AI**.  
The system is designed as a conversational tutor: it guides users through structured learning paths, evaluates responses, recommends next steps, and can process uploaded files (documents, code, and images) to provide context-aware assistance.

---

## Features

- Conversational learning assistant with persistent memory  
- Predefined learning paths (Programming, Data Science, Web Development)  
- File upload support:
  - Documents: `.pdf`, `.docx`, `.txt`
  - Source code: `.py`, `.c`, `.cpp`, `.java`
  - Images: `.png`, `.jpg`, `.jpeg`
- Modern chat interface with:
  - Dark and light themes
  - Code highlighting with copy-to-clipboard
  - File attachment preview
- Deployed on Defang.io deployment environment

---

## Architecture

- **Backend**: Flask application with LangGraph for conversational state flow and LangChain integration for Gemini API calls.  
- **Frontend**: HTML with TailwindCSS for styling and Prism.js for syntax highlighting.  
- **File Processing**:
  - PDF parsing via `PyPDF2`
  - DOCX parsing via `python-docx`
  - Plain text extraction for source code files
  - Image handling with Gemini vision model (base64 encoding)  

---


