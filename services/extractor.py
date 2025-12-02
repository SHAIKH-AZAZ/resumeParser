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
You are an advanced resume parser. Follow these rules strictly:

1. Extract all fields according to the provided JSON schema.

2. Do NOT guess missing information. If the resume does not explicitly contain a field, return an empty string.

3. Infer district/state from address text when possible using normal geographical knowledge.

4. Infer total experience by calculating from all job durations only when not explicitly stated.

5. Infer date of birth ONLY when explicitly visible (DOB, Date of Birth, Born on).

6. EDUCATION RULE (IMPORTANT):
   - Extract full education history into the `education` array normally.
   - Then identify the candidate’s **latest / highest qualification**.
   - “Latest” means:
       a) Most recent year (e.g., 2024 > 2022 > 2019)
       b) If years unclear, use hierarchy:
          MBA/Masters > B.Tech/B.E/B.Com/BCA > Diploma > 12th > 10th.
   - For the main field `education`, return ONLY the latest qualification in this exact format:
        "{degree} - {institute} ({year})"
     Example: "MBA - NMIMS (2024)"  
   - If year is a range (07/2022–04/2024), take the ending year (2024).

7. EXPERIENCE RULE (IMPORTANT):
   - For each entry in `experience_details`, create a concise summary.
   - Keep each summary **only 1–2 lines**, maximum 3 short points.
   - Focus ONLY on the most impactful responsibilities.
   - DO NOT include long paragraphs or detailed descriptions.
   - Avoid excessive bullet points, jargon, tools, and long workflows.
   - The goal: clean, readable, high-level summaries only.

   Example transformation:
      ❌ Too detailed:
         "Designed workflows... managed 36-member team... conducted UAT... created dashboards..."

      ✔ Correct concise version:
         "Led agile delivery for digital platforms; managed 36-member cross-functional team; handled UAT and reporting."

8. Ensure the output JSON strictly follows the schema with no additional fields.

9. Do NOT fabricate institute names, dates, qualifications, or job roles.

10. The final JSON must be clean, concise, and ready for CSV generation.

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
