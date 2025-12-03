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
You are an advanced resume parser. Follow all rules strictly and output ONLY valid JSON.

RULE 1 — SCHEMA COMPLIANCE
• Extract every field exactly as defined in the JSON schema.
• Types must match: strings stay strings, arrays stay arrays, objects stay objects.
• Do not add new fields. Do not remove fields.

RULE 2 — NO GUESSING
• If a field is not explicitly present in the resume, return an empty string.
• Never invent degrees, dates, job titles, employers, locations, or numbers.

RULE 3 — ADDRESS LOGIC
• Infer district and state ONLY from address text when clearly recognizable.
• Use simple, factual inference only. No guessing.

RULE 4 — EXPERIENCE CALCULATION
• If total experience is not explicitly stated, calculate it from job durations.
• If calculation is unclear, leave the field empty.

RULE 5 — DATE OF BIRTH
• Extract DOB ONLY if clearly written (e.g., “DOB”, “Date of Birth”, “Born on”).
• Never approximate or infer DOB.

RULE 6 — EDUCATION PROCESSING
1. Extract the full education list into the "education" array.
2. Determine the latest or highest qualification by:
   • Most recent year, OR
   • Hierarchy if year is missing:
     Masters/MBA > B.Tech/B.E/B.Com/B.Sc/BCA > Diploma > 12th > 10th.
3. In the main "education" field, output ONLY the latest qualification as:
      "{degree} - {institute} ({year})"
4. If the year is a range (e.g., "2022–2024"), use the ending year.

RULE 7 — EXPERIENCE SUMMARIZATION
• For each job, create a short summary (1–2 lines maximum).
• Include only the most important responsibilities.
• Summaries must be concise and readable.
• No long paragraphs, no lists of tools, no unnecessary details.

RULE 8 — OUTPUT FORMAT
• Output MUST be valid JSON only.
• No markdown.
• No explanation.
• No text before or after the JSON.
• Do not wrap the JSON in code blocks.

RULE 9 — RELIABILITY
• If any part of the resume is ambiguous, leave the field empty.
• Never fabricate information.

Follow all rules exactly. Produce clean, minimal, strictly structured JSON.

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
