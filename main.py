import json
import pandas as pd
from tqdm import tqdm
import os 
from config import INPUT_FOLDER, OUTPUT_JSON_FOLDER, OUTPUT_CSV_FOLDER
from services.pdf_reader import extract_text_from_pdf
from services.text_cleaner import clean_text
from services.file_utils import list_pdf_files
from services.extractor import extract_resume_data


def flatten_json_for_csv(data):
    data["education"] = json.dumps(data["education"])
    data["experience_details"] = json.dumps(data["experience_details"])
    return data


def main():
    pdf_files = list_pdf_files(INPUT_FOLDER)
    rows = []

    for pdf in tqdm(pdf_files, desc="Processing Resumes"):
        file_name = os.path.basename(pdf)

        text = extract_text_from_pdf(pdf)
        clean = clean_text(text)

        json_data = extract_resume_data(clean, file_name)

        # Save raw JSON
        with open(f"{OUTPUT_JSON_FOLDER}/{file_name.replace('.pdf','.json')}", "w") as f:
            json.dump(json_data, f, indent=4)

        rows.append(flatten_json_for_csv(json_data))

    # Save CSV
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT_CSV_FOLDER}/final_output.csv", index=False)

    print("\n✔ DONE! Resume extraction completed successfully.")


if __name__ == "__main__":
    main()
