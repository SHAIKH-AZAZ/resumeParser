import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-5-nano"  # or gpt-4.1-mini for cheaper

INPUT_FOLDER = "input/resumes"
OUTPUT_TEXT_FOLDER = "output/text"
OUTPUT_JSON_FOLDER = "output/json"
OUTPUT_CSV_FOLDER = "output/csv"
LOG_FILE = "logs/app.log"
