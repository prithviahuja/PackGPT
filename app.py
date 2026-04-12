import streamlit as st
import requests
import json
import pyperclip

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Context Compression Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { font-family: monospace; font-size: 13px; }
    .context-pack {
        background: #1a1a2e;
        border: 1px solid #16213e;
        border-left: 4px solid #0f3460;
        border-radius: 8px;
        padding: 1.5rem;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        white-space: pre-wrap;
        color: #e0e0e0;
    }
    .stat-card {
        background: #1a1a2e;
        border: 1px solid #16213e;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stat-number { font-size: 2rem; font-weight: bold; color: #e94560; }
    .stat-label { font-size: 0.8rem; color: #888; }
    .tag {
        display: inline-block;
        background: #0f3460;
        color: #e0e0e0;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
    }
    h1 { color: #e94560 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("API Key (Optional)", type="password", placeholder="Gemini or Groq key...", help="Leave blank to use server-side .env key")
    model = st.selectbox("Model", [
        "gemini-3-flash-preview",
        "llama-3.3-70b-versatile"
    ], help="Llama = Fast/Concise | Gemini = Large/Detailed")
    
    st.info("""
    💡 **Quick Guide:**
    - **Llama 3.3**: Fast, concise results for smaller inputs.
    - **Gemini 3**: Massive context support for large inputs & detailed results.
    """)
    
    st.markdown("---")
    st.markdown("### 📖 How to use")
    st.markdown("""
1. Paste your full chat history below
2. Enter API key (or leave blank for default)
3. Click **Compress**
4. Copy the Context Pack into a new chat
    """)
    st.markdown("---")
    st.caption("Context Compression Engine v1.1 (Gemini & Groq)")

st.title("🧠 Context Compression Engine")
st.markdown("*Transform thousands of lines of chat history into structured, reusable intelligence.*")

chat_text = st.text_area(
    "Paste your full chat history here",
    height=300,
    placeholder="Paste your ChatGPT / Claude conversation here...\n\nUser: ...\nAssistant: ...",
    help="Supports ChatGPT and Claude chat formats. Paste the full conversation."
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    compress_btn = st.button("🚀 Compress", type="primary", use_container_width=True)
with col2:
    extract_btn = st.button("🔬 Extract JSON Only", use_container_width=True)

if compress_btn or extract_btn:
    if not chat_text.strip():
        st.error("Please paste some chat text first.")
    else:
        endpoint = "/compress" if compress_btn else "/extract"
        with st.spinner("🔄 Processing..."):
            try:
                payload = {"chat_text": chat_text, "model": model}
                if api_key.strip():
                    payload["api_key"] = api_key
                
                resp = requests.post(
                    f"{API_BASE}{endpoint}",
                    json=payload,
                    timeout=120
                )
                resp.raise_for_status()
                result = resp.json()
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
                st.stop()
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ API error: {e.response.text}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.stop()

        st.success("✅ Compression complete!")

        if compress_btn and "stats" in result:
            stats = result["stats"]
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["input_chars"]:,}</div><div class="stat-label">Input Characters</div></div>', unsafe_allow_html=True)
            with s2:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["output_chars"]:,}</div><div class="stat-label">Output Characters</div></div>', unsafe_allow_html=True)
            with s3:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["compression_ratio"]}x</div><div class="stat-label">Compression Ratio</div></div>', unsafe_allow_html=True)
            with s4:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["chunks_processed"]}</div><div class="stat-label">Chunks Processed</div></div>', unsafe_allow_html=True)

            st.markdown("---")

        structured = result.get("structured", {})

        if compress_btn and "context_pack" in result:
            tab1, tab2 = st.tabs(["📦 Context Pack", "🔬 Structured JSON"])
        else:
            tab1 = None
            tab2 = st.container()

        if compress_btn and "context_pack" in result:
            with tab1:
                st.markdown("### 📦 Context Pack")
                st.markdown("*Copy this entire block and paste it at the start of your new chat.*")
                context_pack = result["context_pack"]
                st.markdown(f'<div class="context-pack">{context_pack}</div>', unsafe_allow_html=True)
                st.markdown("")
                if st.button("📋 Copy Context Pack to Clipboard"):
                    try:
                        pyperclip.copy(context_pack)
                        st.success("Copied!")
                    except Exception:
                        st.text_area("Copy manually:", value=context_pack, height=200)

        with tab2 if compress_btn else tab2:
            st.markdown("### 🔬 Structured Intelligence")

            if structured.get("user_goal"):
                st.markdown("#### 🎯 User Goal")
                st.info(structured["user_goal"])

            if structured.get("tech_stack"):
                st.markdown("#### 🛠 Tech Stack")
                tags_html = " ".join([f'<span class="tag">{t}</span>' for t in structured["tech_stack"]])
                st.markdown(tags_html, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if structured.get("decisions"):
                    st.markdown("#### 🧭 Decisions Made")
                    for d in structured["decisions"]:
                        st.markdown(f"- {d}")

                if structured.get("constraints"):
                    st.markdown("#### ⛓ Constraints")
                    for c in structured["constraints"]:
                        st.markdown(f"- {c}")

            with col_b:
                if structured.get("problems"):
                    st.markdown("#### ❌ Problems / Errors")
                    for p in structured["problems"]:
                        st.markdown(f"- {p}")

                if structured.get("solutions"):
                    st.markdown("#### ✅ Solutions Applied")
                    for s in structured["solutions"]:
                        st.markdown(f"- {s}")

            if structured.get("notes"):
                st.markdown("#### 📌 Important Notes")
                for n in structured["notes"]:
                    st.markdown(f"- {n}")

            if structured.get("code_snippets"):
                st.markdown("#### 💻 Key Code Snippets")
                for snippet in structured["code_snippets"]:
                    with st.expander(f"📄 {snippet.get('label', 'Snippet')}"):
                        st.code(snippet.get("code", ""), language="python")

            st.markdown("#### 📋 Raw JSON")
            with st.expander("View raw structured JSON"):
                st.json(structured)
                if st.button("📋 Copy JSON"):
                    try:
                        pyperclip.copy(json.dumps(structured, indent=2))
                        st.success("Copied!")
                    except Exception:
                        st.text_area("Copy manually:", value=json.dumps(structured, indent=2), height=200)
