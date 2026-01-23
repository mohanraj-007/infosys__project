import os
import ast
import re
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN is missing. Add it in Streamlit Secrets.")
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=HF_TOKEN
)
def is_valid_python(code: str) -> bool:
    try:
        compile(code, "<user_code>", "exec")
        return True
    except Exception:
        return False


def is_meaningful_python(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    if len(tree.body) == 1:
        node = tree.body[0]
        if isinstance(node, ast.Expr) and isinstance(node.value, (ast.Name, ast.Constant)):
            return False
    return True


def remove_repetition(text: str) -> str:
    sections = [
        "ISSUES & IMPROVEMENTS",
        "CORRECTED CODE",
        "OPTIMIZED CODE"
    ]

    seen = set()
    result = []

    for line in text.splitlines():
        header = line.strip()
        if header in sections:
            if header in seen:
                break
            seen.add(header)
        result.append(line)

    return "\n".join(result).strip()

def get_ai_suggestions(code_string: str):
    if not code_string.strip():
        return []

    if not is_valid_python(code_string) or not is_meaningful_python(code_string):
        return [{
            "type": "Error",
            "message": "Please enter valid Python code (example: print('hi')).",
            "severity": "High"
        }]
    prompt = f"""
You are a Python Code Reviewer.

STRICT OUTPUT FORMAT (DO NOT BREAK):

ISSUES & IMPROVEMENTS
- bullet points OR "No issues found."

CORRECTED CODE
- Python code block OR "No correction needed."

OPTIMIZED CODE
- Python code block OR "The corrected code is already optimal."

Analyze ONLY this code:

```python
{code_string}
"""
    try:
        response = client.chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.0
        )
    
        
        response_text = response.choices[0].message.content

    
        cleaned = remove_repetition(response_text)

        return [{
            "type": "AISuggestion",
            "message": cleaned,
            "severity": "Info"
        }]
    
    except Exception as e:
        return [{
            "type": "Error",
            "message": str(e),
            "severity": "High"
        }]
