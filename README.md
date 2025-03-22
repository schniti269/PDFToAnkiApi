# PDF to Anki API

A FastAPI-based web service that automatically converts PDF documents into Anki-compatible flashcards using AI.

## Overview

This application was built to work with Apple Shortcuts, enabling users to share PDFs directly with the API and receive ready-to-import Anki flashcards. This solves the problem of Apple Shortcuts lacking the processing power and capabilities needed to handle complex document parsing and multiple API calls.

## Features

- **PDF Text Extraction**: Extracts text content from uploaded PDF documents
- **AI-Powered Flashcard Generation**: Uses OpenAI's API to intelligently create question-answer pairs
- **Parallel Processing**: Efficiently handles large documents through concurrent processing
- **Anki-Compatible Output**: Returns a CSV file that can be directly imported into Anki
- **Docker Support**: Easily deployable via Docker on any platform

## How It Works

1. User uploads a PDF document along with their OpenAI API key
2. The API extracts text from the PDF using pdfplumber
3. Text segments are processed in parallel via ThreadPoolExecutor
4. Each segment is sent to OpenAI's API to generate flashcard content
5. Results are formatted into a CSV file compatible with Anki
6. The CSV file is returned to the user for import into Anki

## Requirements

- Python 3.8+
- FastAPI
- OpenAI API key
- pdfplumber
- uvicorn

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/PDFToAnkiApi.git
cd PDFToAnkiApi

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Docker Deployment

```bash
# Build the Docker image
docker build -t pdf-to-anki-api .

# Run the container
docker run -p 8000:8000 pdf-to-anki-api
```

## Usage

### API Endpoints

- **POST /PDF2Flashcard**: Main endpoint for processing PDFs
  - Parameters:
    - `api_key`: Your OpenAI API key (form field)
    - `pdf_file`: The PDF file to process (file upload)
  - Returns: CSV file with flashcards

- **POST /test**: Test endpoint that returns sample flashcards
  - Parameters:
    - `api_key`: Your OpenAI API key (form field)
    - `pdf_file`: Any PDF file (not processed, just for testing)
  - Returns: Sample cards.csv file

### Example with curl

```bash
curl -X POST "http://localhost:8000/PDF2Flashcard" \
  -F "api_key=your-openai-api-key" \
  -F "pdf_file=@/path/to/your/document.pdf" \
  --output "flashcards.csv"
```

### Apple Shortcuts Integration

1. Create a new shortcut in the Apple Shortcuts app
2. Add the "Get Contents of URL" action
3. Set the URL to your deployed API endpoint
4. Configure the request as a POST with multipart form data
5. Add your PDF as the file input and your API key as a text field
6. Add actions to save and process the returned CSV file

## Sample Output

The API generates flashcards in the following format:

```csv
front,back
"What is a PDF to Anki API?","A service that converts PDF documents into Anki-compatible flashcards using AI technology."
"What is the main benefit of using this API with Apple Shortcuts?","It offloads the processing-intensive tasks of PDF parsing and API calls to a server, allowing complex workflows that would be impossible within Apple Shortcuts alone."
```

## Deployment Options

- **Home Server**: Run on a local server within your network
- **Cloud Deployment**: Deploy to AWS Lambda, Google Cloud Functions, or similar serverless platforms
- **Docker Container**: Run in any environment that supports Docker

## License

MIT

## Future Improvements

- Support for more document formats (DOCX, EPUB, etc.)
- Custom flashcard templates
- Enhanced error handling and feedback
- Support for newer OpenAI models
- User authentication for shared deployments 