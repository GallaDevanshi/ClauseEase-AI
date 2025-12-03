# ClauseEase-AI

📘 Document Translation & Chat Assistant (Streamlit + Ollama)

This project is a Streamlit-based smart chatbot that allows users to upload documents (PDF, TXT, CSV) and instantly translate or summarize them into English using a local Ollama LLM model.
It also includes multi-chat support, persistent session history, custom chat UI styling, and context-aware responses powered by the uploaded file.

Features

1️. Multi-Chat System

Create new chats

Switch between chat histories

Messages saved in session_state to prevent loss on page reload

2️. Advanced File Upload & Extraction

Supports:

PDF files (via PyPDF2)

TXT & CSV files (multi-encoding support)

File extraction flow:

Detect file type

Extract text

Store it in st.session_state.file_text

Display preview & enable translation

3️. Document Translation to English

You can upload documents in any language (Hindi, Telugu, Tamil, Marathi, Arabic, French, etc.).

The app:

Extracts text

Sends it to a local Ollama model

Returns:

A clear English summary (4–6 sentences)

6–10 bullet-point insights

Fully offline & privacy-safe since processing happens locally

4️. Chatbot with Context Awareness

User messages displayed as right-aligned bubbles

Assistant messages left-aligned with soft styling

If a file is uploaded, the assistant uses the first 2000 characters as reference

Gives explanations, breakdowns, and Q&A from the document

5️.Sidebar Utilities

Upload documents

View chat history

Buttons for:

Summarize file

Insert summary into chat

Clear file & summary

Preview of extracted text and summary

How It Works

1.Upload a document

2.App extracts text

3.Text is summarized & translated using ollama.chat()

4.Summary shown in UI or inserted into chat

5.You can chat with the assistant using the document context
