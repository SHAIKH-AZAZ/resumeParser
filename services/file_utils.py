import os

def list_pdf_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".pdf")]


