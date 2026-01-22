import streamlit as st
import time
from parse import parse_code
from error_detector import detect_errors
from ai_suggestion import get_ai_suggestions
import os
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.environ.get("HF_TOKEN")
st.set_page_config(
    page_title="AI Code Reviewer Application",
    page_icon="🤖",
    layout="wide"
)
if "code_input" not in st.session_state:
    st.session_state.code_input = ""
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "ai_trigger" not in st.session_state:
    st.session_state.ai_trigger = 0
def reset_app():
    st.session_state.code_input = ""
    st.session_state.analyzed = False
    st.session_state.ai_trigger = 0
def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)
st.markdown("""
<style>
.chat-message {
    padding: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
col1, col2 = st.columns([1, 5])
with col1:
    st.image("download.png", width=90)
with col2:
    st.markdown("## 🤖 AI Code Reviewer")
    st.caption("Analyze • Improve • Optimize your Python code")
# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["🧪 Code Review", "🤖 AI Suggestions"])
with tab1:
    st.markdown(
        "Paste your **Python code** below and click **Analyze** to check syntax and static issues."
    )
    code = st.text_area(
        "Code Input:",
        height=220,
        key="code_input"
    )
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        analyze_clicked = st.button("Analyze", type="primary")
    with col2:
        st.button("Refresh", on_click=reset_app)
    if analyze_clicked:
        if not code.strip():
            st.warning("⚠️ Please enter some Python code.")
            st.stop()
        parse_result = parse_code(code)

        if not parse_result["success"]:
            st.error("❌ Syntax Error Detected")
            st.code(
                f"Line {parse_result['error']['line']}: "
                f"{parse_result['error']['message']}"
            )
            st.stop()
        st.success("✅ Code parsed successfully!")
        st.session_state.analyzed = True
        # Static Analysis
        st.subheader("📊 Static Code Analysis")
        error_result = detect_errors(code)
        if error_result["success"]:
            if error_result["error_count"] == 0:
                st.info("🎉 No static issues found.")
            else:
                st.warning(f"⚠️ Found {error_result['error_count']} issue(s):")

                for error in error_result["errors"]:
                    with st.expander(
                        f"{error['type']} (Line {error['line']})",
                        expanded=True
                    ):
                        st.write(f"**Message:** {error['message']}")
                        st.info(f"**Suggestion:** {error['suggestion']}")
        else:
            st.error("❌ Static analysis failed.")
with tab2:
    if not st.session_state.analyzed:
        st.info("ℹ️ Analyze the code first to get AI suggestions.")
    else:
        col1, col2 = st.columns([2, 8])
        with col1:
            if st.button("🔁 Re-Suggest", type="secondary"):
                st.session_state.ai_trigger += 1
        with col2:
            st.caption("Click to regenerate AI suggestions")
        with st.spinner("🤖 Generating AI suggestions..."):
            # ai_trigger forces rerun
            _ = st.session_state.ai_trigger
            suggestions = get_ai_suggestions(
                st.session_state.code_input
            )
            for suggestion in suggestions:
                if suggestion["type"] == "AISuggestion":
                    with st.chat_message("assistant"):
                        st.write_stream(
                            stream_data(suggestion["message"])
                        )
                else:
                    st.error(suggestion["message"])
