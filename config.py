import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite"  # using this for free teir  ,cheaper

INPUT_FOLDER = "input/resumes"
OUTPUT_TEXT_FOLDER = "output/text"
OUTPUT_JSON_FOLDER = "output/json"
OUTPUT_CSV_FOLDER = "output/csv"
LOG_FILE = "logs/app.log"
