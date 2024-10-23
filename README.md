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

## Create a .spec file

`pyi-makespec --name WhisperTranscriber --windowed whisper_app.py`

## Adjust the .spec file

```
# -*- mode: python ; coding: utf-8 -*-
import os

# Define the output paths
user_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
whisper_transcriber_path = os.path.join(user_downloads, 'WhisperTranscriber')

# Ensure the download directory exists
os.makedirs(whisper_transcriber_path, exist_ok=True)

# Define build path within the WhisperTranscriber folder
build_path = os.path.join(whisper_transcriber_path, 'build')
os.makedirs(build_path, exist_ok=True)

a = Analysis(
    ...
    datas=[
        ('.venv/Lib/site-packages/whisper', 'whisper'),
    ],
    ...
)

pyz = PYZ(a.pure)

exe = EXE(
    ...
    name='WhisperAudioTranscriber',
    ...
    distpath=dist_path,  # Specify custom dist path
)
coll = COLLECT(
    ...
    name='WhisperAudioTranscriber',
    distpath=dist_path,  # Specify custom dist path
)
```

## Build the application

`pyinstaller WhisperTranscriber.spec`
