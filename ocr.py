from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import re

model= ocr_predictor(pretrained=True)


def extractpdf():

    doc = DocumentFile.from_pdf("pdf/document.pdf")


    result= model(doc)

    text = result.render()

    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    dates = re.findall(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b", text)
    mesures = re.findall(r"\b\d+(?:[.,]\d+)?\s*(?:mSv/h|µSv/h|mSv|µSv|Bq|°C|bar)\b", text, re.IGNORECASE)
    references = re.findall(r"\b(?:RAP|REF|DOC)-\d+\b", text, re.IGNORECASE)
    

    donnees = {
        "emails": emails,
        "dates": dates,
        "mesures": mesures,
        "references": references,
    }

    print("--- TEXTE EXTRAIT ---")
    print(text)
    print("\n--- CHAMPS REGEX ---")
    print(donnees)

    return donnees


extractpdf()
