import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
import os

# Load schema
schema_path = os.path.join(os.path.dirname(__file__), "..", "schema", "resume_schema.json")
schema_path = os.path.abspath(schema_path)

with open(schema_path, "r", encoding="utf-8") as f:
    resume_schema = json.load(f)

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are an advanced resume parser.

Follow these rules strictly:

1. Extract all fields according to the provided JSON schema.
2. NEVER guess missing information. If the resume does not mention a field, return an empty string.
3. Infer district and state from any available address text using common geographical knowledge.
4. Infer total years of experience by calculating from all employment durations when the resume does not explicitly mention it.
5. Infer date of birth ONLY if explicitly present in the text (e.g., DOB, born on, date of birth).
6. EDUCATION RULE:
   - Extract full education history into the `education` array as normal.
   - But for the top-level `education` field in the final schema, ONLY return the LATEST/HIGHEST qualification.
   - Latest means the most recent year OR the highest level (postgraduate > graduate > diploma > school).
   - Do not list multiple degrees in the top-level field.
   - If the year is missing, infer order based on hierarchy (MBA > B.Tech > Diploma > 12th > 10th).
7. Do not hallucinate or fabricate names of institutions, dates, or qualifications.
8. The output JSON must strictly follow the provided schema structure.
9. If a field is not present in the resume, return an empty string. 

"""

def extract_resume_data(text, file_name):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""
Extract resume fields according to this JSON schema:

{json.dumps(resume_schema)}

FILE NAME: {file_name}

RESUME TEXT:
{text}
"""
            }
        ],
        response_format={"type": "json_object"}
    )

    json_output = response.choices[0].message.content
    return json.loads(json_output)
