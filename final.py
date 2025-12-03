import streamlit as st
import PyPDF2
from ollama import chat, ResponseError  # ✅ Ollama client

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Chatbot", layout="wide")

# --- CUSTOM CSS FOR CHAT ALIGNMENT ---
st.markdown("""
<style>
.stChatMessage.user {
    flex-direction: row-reverse !important;
    text-align: right !important;
    background-color: rgba(0, 123, 255, 0.10) !important;
    border-radius: 15px !important;
    padding: 10px !important;
    margin-bottom: 1rem !important;
}
.stChatMessage.assistant {
    flex-direction: row !important;
    text-align: left !important;
    background-color: rgba(248, 249, 250, 0.80) !important;
    border-radius: 15px !important;
    padding: 10px !important;
    margin-bottom: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None
if "file_text" not in st.session_state:
    st.session_state.file_text = ""
if "file_summary" not in st.session_state:
    st.session_state.file_summary = ""

# --- SIDEBAR - CHAT HISTORY ---
st.sidebar.title("📚 Chat History")
for title in list(st.session_state.chats.keys()):
    if st.sidebar.button(title):
        st.session_state.active_chat = title
        st.session_state.messages = st.session_state.chats[title]
if st.sidebar.button("➕ New Chat"):
    st.session_state.active_chat = None
    st.session_state.messages = []
    st.session_state.file_text = ""
    st.session_state.file_summary = ""

# --- FILE UPLOAD HANDLING ---
uploaded_file = st.sidebar.file_uploader("📁 Upload File", type=["txt", "csv", "pdf"]) 
if uploaded_file:
    file_text = ""
    # PDF Handling
    if uploaded_file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    pdf_text.append(text)
            file_text = "\n".join(pdf_text) if pdf_text else ""
            st.session_state.file_text = file_text
            st.sidebar.success("✅ PDF file loaded successfully!")
        except Exception as e:
            st.session_state.file_text = ""
            st.sidebar.error(f"❌ Could not read PDF: {e}")
    else:
        # Other text/csv files
        file_bytes = uploaded_file.getvalue()
        for enc in ["utf-8", "utf-16", "cp1252", "latin1"]:
            try:
                file_text = file_bytes.decode(enc)
                st.session_state.file_text = file_text
                st.sidebar.success("✅ Text file loaded successfully!")
                break
            except UnicodeDecodeError:
                continue
        if not file_text:
            st.session_state.file_text = file_bytes.decode("utf-8", errors="ignore")
            st.sidebar.warning("⚠️ File decoded with fallback encoding.")

    # Optionally: auto-generate a short preview summary (non-blocking best-effort)
    # We provide an explicit button below so the user controls generation; this auto-preview remains empty until they click.

# --- SUMMARY UTILITIES ---

def summarize_text_with_ollama(text: str, model_name: str = "llama3.1:8b", max_chars: int = 20000) -> str:
    """Call the Ollama model to summarize the provided text in English.

    We limit the input length to max_chars characters to avoid sending extremely large payloads.
    """
    if not text:
        return ""

    truncated = text[:max_chars]
    system_prompt = (
    "You are a helpful assistant. The input text may be in any language. "
    "Your task is to generate the summary ONLY in English, regardless of the input language. "
    "Do NOT use any words or sentences from the original language. "
    "Write a 4–6 sentence English summary and then 6–10 bullet points of key insights. "
    "Use simple English suitable for beginners."
)

    model_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": truncated}
    ]

    try:
        response = chat(model=model_name, messages=model_messages, stream=False)
        return response.get("message", {}).get("content", "⚠️ No reply from model.")
    except ResponseError as e:
        return f"⚠️ Ollama error: {e}"
    except Exception as e:
        return f"⚠️ Connection error: {e}"

# --- SUMMARY BUTTONS IN SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.header("📄 File Summary")
if st.sidebar.button("🔎 Summarize file (English)"):
    if st.session_state.file_text:
        with st.spinner("Summarizing file in English..."):
            st.session_state.file_summary = summarize_text_with_ollama(st.session_state.file_text, max_chars=20000)
        st.sidebar.success("✅ Summary generated.")
    else:
        st.sidebar.warning("Upload a file first to summarize.")

if st.sidebar.button("📝 Insert summary into chat"):
    if st.session_state.file_summary:
        # Append the summary as an assistant message so it shows up in chat
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.file_summary})
        st.session_state.chats[st.session_state.active_chat or "Chat"] = list(st.session_state.messages)
        st.sidebar.success("Inserted summary into chat.")
    else:
        st.sidebar.warning("Generate a summary first.")

if st.session_state.file_summary:
    # Show a small preview of the summary in sidebar (first 800 chars)
    st.sidebar.subheader("Preview")
    st.sidebar.write(st.session_state.file_summary[:800])
    if len(st.session_state.file_summary) > 800:
        st.sidebar.markdown("*...summary truncated in preview — insert into chat or open full summary.*")

# --- MAIN CHAT INTERFACE ---
st.title("CHATBOT")

# If a file is uploaded, optionally show filename preview and a concise "Generate and insert" quick action
if uploaded_file:
    with st.expander("Uploaded file preview / quick actions", expanded=False):
        st.write("File preview (first 1500 characters):")
        st.code(st.session_state.file_text[:1500])
        cols = st.columns([1, 1, 1])
        if cols[0].button("Summarize (and show)"):
            with st.spinner("Summarizing file in English..."):
                st.session_state.file_summary = summarize_text_with_ollama(st.session_state.file_text, max_chars=20000)
        if cols[1].button("Summarize & insert to chat"):
            if st.session_state.file_text:
                with st.spinner("Summarizing and inserting into chat..."):
                    st.session_state.file_summary = summarize_text_with_ollama(st.session_state.file_text, max_chars=20000)
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.file_summary})
                st.session_state.chats[st.session_state.active_chat or "Chat"] = list(st.session_state.messages)
        if cols[2].button("Clear file & summary"):
            st.session_state.file_text = ""
            st.session_state.file_summary = ""
            st.sidebar.success("Cleared uploaded file and summary.")

for msg in st.session_state.messages:
    css_class = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(msg["role"]):
        st.markdown(
            f"<div class='stChatMessage {css_class}'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# --- CHAT INPUT ---
user_input = st.chat_input("Type your message...")

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # ✅ Build model input messages
    system_prompt = "You are a helpful AI assistant. Answer concisely and clearly."
    if st.session_state.file_text:
        context_preview = st.session_state.file_text[:2000]  # Limit to first 2k chars
        system_prompt += f"\n\nHere’s some reference text from the uploaded file (use it if relevant):\n{context_preview}"

    # Build conversation for model
    model_messages = [
        {"role": "system", "content": system_prompt}
    ] + st.session_state.messages[-10:]  # last 10 exchanges

    # --- CALL OLLAMA MODEL ---
    try:
        with st.spinner("🤖 Thinking..."):
            response = chat(
                model="llama3.2:1b",  # ✅ Use your pulled model name
                messages=model_messages,
                stream=False
            )
        bot_reply = response.get("message", {}).get("content", "⚠️ No reply from model.")
    except ResponseError as e:
        bot_reply = f"⚠️ Ollama error: {e}"
    except Exception as e:
        bot_reply = f"⚠️ Connection error: {e}"

    # Append bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # --- DISPLAY LAST EXCHANGE ---
    for idx in [-2, -1]:
        msg = st.session_state.messages[idx]
        css_class = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(msg["role"]):
            st.markdown(
                f"<div class='stChatMessage {css_class}'>{msg['content']}</div>",
                unsafe_allow_html=True
            )

    # --- UPDATE CHAT HISTORY ---
    if not st.session_state.active_chat:
        first_word = user_input.split()[0] if user_input.strip() else "Chat"
        st.session_state.active_chat = first_word
    st.session_state.chats[st.session_state.active_chat] = list(st.session_state.messages)

# --- Display full generated summary in main area (optional)
if st.session_state.file_summary:
    st.markdown("---")
    st.subheader("Summary (English)")
    st.write(st.session_state.file_summary)
    # Provide download option
    st.download_button("Download summary (TXT)", st.session_state.file_summary, file_name="summary.txt")
