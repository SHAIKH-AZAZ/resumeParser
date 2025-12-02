import json
import pandas as pd
from tqdm import tqdm
import os 
from config import INPUT_FOLDER, OUTPUT_JSON_FOLDER, OUTPUT_CSV_FOLDER
from services.pdf_reader import extract_text_from_pdf
from services.text_cleaner import clean_text
from services.file_utils import list_pdf_files
from services.extractor import extract_resume_data


# FIXED: Remove bad unicode decoding
def clean_unicode(value):
    return value  # NEVER decode again — this prevents “â€”” errors


def flatten_json_for_csv(data):

    # Clean simple fields
    for key in data:
        if isinstance(data[key], str):
            data[key] = clean_unicode(data[key])

    # Format education (latest degree already applied from GPT)
    if isinstance(data.get("education"), list) and len(data["education"]) > 0:
        edu = data["education"][0]
        degree = edu.get("degree", "")
        institute = edu.get("institute", "")
        year = edu.get("year", "")
        data["education"] = f"{degree}\n{institute}\n{year}"
    else:
        data["education"] = ""

    # Format experience (multi-line clean)
    exp_list = data.get("experience_details", [])
    exp_formatted = []

    for i, exp in enumerate(exp_list, start=1):
        block = (
            f"{i}) {exp.get('company_name', '')} — {exp.get('role', '')} ({exp.get('duration', '')})\n"
            f"   - {exp.get('responsibilities', '')}"
        )
        exp_formatted.append(block)

    data["experience_details"] = "\n\n".join(exp_formatted)

    return data


def main():
    pdf_files = list_pdf_files(INPUT_FOLDER)
    rows = []

    for pdf in tqdm(pdf_files, desc="Processing Resumes"):
        file_name = os.path.basename(pdf)

        text = extract_text_from_pdf(pdf)
        clean = clean_text(text)

        json_data = extract_resume_data(clean, file_name)

        # Save raw JSON (UTF-8 safe)
        with open(f"{OUTPUT_JSON_FOLDER}/{file_name.replace('.pdf','.json')}", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        rows.append(flatten_json_for_csv(json_data))

    # Save final CSV (UTF-8 SAFE)
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT_CSV_FOLDER}/final_output.csv", index=False, encoding="utf-8")

    print("\n✔ DONE! Resume extraction completed successfully.")


if __name__ == "__main__":
    main()
