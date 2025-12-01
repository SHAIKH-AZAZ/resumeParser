def clean_text(text):
    text = text.replace("\t", " ")
    text = " ".join(text.split())
    return text
