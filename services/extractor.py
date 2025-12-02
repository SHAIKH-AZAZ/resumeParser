import json
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME
import os
import re



def extract_json(text):
    """Extract the first valid JSON block from Gemini output."""
    # Find JSON using regex
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None

# Load schema
schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "resume_schema.json")
schema_path = os.path.abspath(schema_path)

with open(schema_path, "r", encoding="utf-8") as f:
    resume_schema = json.load(f)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)


SYSTEM_PROMPT = """
You are an advanced resume parser. Follow these rules strictly:

1. Extract all fields according to the provided JSON schema.
2. Do NOT guess missing information. If the resume does not explicitly contain a field, return an empty string.
3. Infer district/state from address text when possible.
4. Infer total experience by calculating durations when not explicitly stated.
5. Infer DOB ONLY when explicitly visible.

6. EDUCATION RULE:
   - Extract full education history into the "education" array.
   - Identify the latest / highest qualification (most recent year OR highest hierarchy).
   - Return ONLY that latest qualification in this format:
        "{degree} - {institute} ({year})"
   - If year is a range (2022–2024), take the ending year.

7. EXPERIENCE RULE:
   - Summaries must be short (1–2 lines each, max 2 points).
   - NO lengthy paragraphs, as short as possible .
   - Focus only on the most important responsibilities, so list only those .

8. Output MUST be VALID JSON ONLY.
9. No comments, no markdown, no explanations — just valid JSON.
"""


def extract_resume_data(text, file_name):

    prompt = f"""
{SYSTEM_PROMPT}

JSON SCHEMA:
{json.dumps(resume_schema)}

FILE NAME:
{file_name}

RESUME TEXT:
{text}

IMPORTANT:
- RESPOND WITH VALID JSON ONLY.
"""


    response = model.generate_content(prompt)

    raw_output = response.text.strip()

    # Extract valid JSON
    json_block = extract_json(raw_output)

    if not json_block:
        raise ValueError(f"Gemini did not return JSON. Raw output:\n{raw_output}")

    # Try to parse
    try:
        return json.loads(json_block)
    except json.JSONDecodeError:
        # Auto-repair common issues: trailing commas, unicode escapes, etc.
        repaired = json_block.replace("\n", "").replace("\t", "").strip()
        return json.loads(repaired)
