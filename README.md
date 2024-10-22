# whisper-transcriber-app

## Activate virtual environment

Windows: `.venv\Scripts\activate`
MacOS: `source .venv/bin/activate`

## Required Packages

`pip install openai-whisper torch torchvision torchaudio PySide6`

## Create a requirements.txt

`pip freeze > requirements.txt`

# Project reduplication

Clone the repo

### requirements.txt

`pip install -r requirements.txt`

## Update Requirements

`python tools/update_requirements.py`

# Run the Application

`python .\whisper_app.py`

# Package

`pip install pyinstaller`

## Create a spec file

`pyi-makespec --name WhisperTranscriber --windowed whisper_app.py`

## Build the application

`pyinstaller WhisperTranscriber.spec`
