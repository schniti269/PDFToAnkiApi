
import concurrent.futures
import csv
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List

import openai
import pdfplumber
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()


# Diese Funktion sollte den Text aus einem PDF extrahieren
def textfrompdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = []
        for page in pdf.pages:
            text += [page.extract_text()]

    return text


async def gpt_flashcards(pages, api_key):
    # Create a ThreadPoolExecutor to parallelize API requests
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit API requests for each segment and store the Future objects
        futures = [executor.submit(make_api_request, segment, api_key) for segment in pages]

        # Initialize an empty list to store flashcards
        flashcard_list = []

        # Iterate through completed Future objects and extract flashcards
        for future in concurrent.futures.as_completed(futures):
            response = await future
            flashcard = extract_flashcard(response)
            flashcard_list.append(flashcard)

    return flashcard_list


def make_api_request(text,api_key):
    prompt = '''Erstelle eine Lernkarte für Anki mit einer Vorder- und Rückseite. Verwende HTML-Tags, um die Karten zu definieren: `<vorn></vorn>` für die Vorderseite und `<hinten></hinten>` für die Rückseite. Geben Sie nur den grundlegenden Karten-Strukturcode zurück.

Für die Frage auf der Vorderseite und die Musterantwort auf der Rückseite könnten folgende Beispiele dienen:
<vorn>Was ist die Hauptstadt von Frankreich?</vorn>
<hinten>Die Hauptstadt von Frankreich ist Paris.</hinten>

Frage auch nach definitionen mit: Erkläre den Begriff, was ist, was ist der Unterschied
Fügen Sie gerne zusätzliches Wissen zum Thema hinzu, aber halten Sie die Karten kurz und prägnant. bitte MAXIMAL eine Karte pro text erstellen! das ist enorm wichtig!
mach lieber eine karte mit zwei ähnlichen fragen ( zum beispiel ein A und B teil)
Solltest du denken dass der Text wenig sinn zu einem konkreten Thema ergibt, dann handelt es sich vermutlich um den text einer Folie mit Bildern oder einer Vorstelldung des Dozenten.
Lass diese Folien bitte aus und gibt -keine inhalte- zurück
die Frage sollte die Zentralen inhalte des textes bestmöglich abdecken.
die Rückseite sollte die Frage beantworten und zusätzliche Informationen enthalten, die Sie sich merken möchten.
solltest du denken, dass der text keine fachlichen bezug hat wie zb vorstellungsrunden oder nur ein name  bitte einfach überspringen und -keine inhalte- zurückgeben
du kannst auch mehrere fragen PRO KARTE erstellen, wenn du denkst dass der text mehrere fragen abdeckt. aber bitte nicht mehr als 3 fragen pro karte
versuch so gut es geht worte aus dem Text zu übernehmen und nicht zu paraphrasieren lass das so wie es ist.
hier ist der text:'''

  # Replace with your OpenAI API key
    openai.api_key = api_key

    response = openai.Completion.create(
        engine="babbage-002",
        temperature = 0,
        max_tokens=1000,
        prompt = prompt+ text
        )
    api_response = response.choices[0].text.strip()

    # Extract the generated text from the OpenAI response
    print("---------------------------")
    print(api_response)
    print("---------------------------")
    return api_response


def extract_flashcard(api_response):

    flashcard = {}
    start_tag = "<vorn>"
    end_tag = "</vorn>"
    back_start_tag = "<hinten>"
    back_end_tag = "</hinten>"

    while start_tag in api_response and end_tag in api_response and back_start_tag in api_response and back_end_tag in api_response:
        start_index = api_response.index(start_tag)
        end_index = api_response.index(end_tag)
        back_start_index = api_response.index(back_start_tag)
        back_end_index = api_response.index(back_end_tag)

        front = api_response[start_index + len(start_tag):end_index]
        back = api_response[back_start_index + len(back_start_tag):back_end_index]

        flashcard={"front": front.strip(), "back": back.strip()}
        print(flashcard)

        # Remove the extracted flashcard from the API response
        api_response = api_response[end_index + len(end_tag):]

    return flashcard



def export_to_csv(flashcards: List[Dict[str, str]]) -> None:
    """Export flashcards to a CSV file."""
    csv_filename = "cards.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ["front", "back"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for flashcard in flashcards:
            writer.writerow(flashcard)

def process_pdf(pdf_path:str,api_key:str) -> None:
    # Ensure the output folder exists

    pages = textfrompdf(pdf_path)
        # Extract flashcards from the PDF
    flashcards = gpt_flashcards(pages,api_key)

        # Export flashcards to a CSV file
    export_to_csv(flashcards)

@app.post("/PDF2Flashcard")
async def process_pdf_endpoint(api_key: str = Form(...), pdf_file: UploadFile = File(...)):

    try:
        # Save the uploaded PDF file to a temporary directory
        pdf_path =  pdf_file.filename
        with open(pdf_path, "wb") as pdf:
            shutil.copyfileobj(pdf_file.file, pdf)

        # Process the PDF file in a separate thread
        with ThreadPoolExecutor() as executor:
            csv_path = await executor.submit(process_pdf, pdf_path, api_key)

        # Return the processed CSV file
        return FileResponse(csv_path, headers={"Content-Disposition": f"attachment; filename=cards.csv"})
    except Exception as e:
        return {"error": str(e)}

@app.post("/test")
async def nothing(api_key: str = Form(...), pdf_file: UploadFile = File(...)):
    return FileResponse("cards.csv", headers={"Content-Disposition": f"attachment; filename=cards.csv"})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

