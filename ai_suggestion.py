import os
import streamlit as st
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage
import re
import referencing
def get_llm():
    api_key = os.getenv("HF_TOKEN") or st.secrets["HF_TOKEN"]
    return HuggingFaceEndpoint(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        api_key=api_key,
        temperature=0.0,
        max_new_tokens=500,
    )

def get_model():
    llm = get_llm()
    return ChatHuggingFace(llm=llm)

model = None
def get_active_model():
    global model
    if model is None:
        model = get_model()
    return model
def is_valid_python(code: str) -> bool:
    try:
        compile(code, "<user_code>", "exec")
        return True
    except Exception:
        return False
def get_ai_suggestions(code_string: str):
    if not code_string.strip():
        return []

    if not is_valid_python(code_string):
        return [{
            "type": "Error",
            "message": "Enter valid Python code, not plain text.",
            "severity": "High"
        }]

    prompt = f"""
You are a STRICT Python Code Reviewer.

Review ONLY the USER CODE.
DO NOT review multiple examples.
DO NOT explain theory.
DO NOT write paragraphs.
DO NOT repeat sections.

MANDATORY FORMAT (NO DEVIATION):

### ISSUES & IMPROVEMENTS
- Bullet points only
- If none: No issues found.

### CORRECTED CODE
- Either code block OR: No correction needed.

### OPTIMIZED CODE
- Either code block OR: The given code is already optimal.

STOP AFTER OPTIMIZED CODE.

### USER CODE
```python
{code_string}
"""
    try:
        model_instance = get_active_model()
        response = model_instance.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        content = re.sub(r"(### [A-Z &]+)-\s*", r"\1\n", content)
        content = re.sub(r"ISSUES\s*&\s*IMPROVEMENTS.*", "### ISSUES & IMPROVEMENTS", content)
        content = re.sub(r"CORRECTED CODE.*", "### CORRECTED CODE", content)
        content = re.sub(r"OPTIMIZED CODE.*", "### OPTIMIZED CODE", content)
        if "### OPTIMIZED CODE" in content:
            before, after = content.split("### OPTIMIZED CODE", 1)
            content = before + "### OPTIMIZED CODE\n" + after.split("###", 1)[0]
        if content.count("### USER CODE") > 1:
            content = content.split("### USER CODE", 1)[0]

        return [{
            "type": "AISuggestion",
            "message": content.strip(),
            "severity": "Info"
        }]

    except Exception as e:
        return [{
            "type": "Error",
            "message": str(e),
            "severity": "High"
        }]
