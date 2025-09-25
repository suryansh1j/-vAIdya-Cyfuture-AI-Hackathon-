import os
import shutil
import subprocess
import json
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
TRANSCRIPTS_DIR = os.path.join(BASE_DIR, "transcripts")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

AUDIO_FILENAME = "Recording.m4a"
AUDIO_PATH = os.path.join(AUDIO_DIR, AUDIO_FILENAME)


@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    with open(AUDIO_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Run the transcription script
        subprocess.run(
            ["python", "../NLP/transcribe_audio.py"],
            check=True,
            capture_output=True,
            text=True,
        )
        # Run the extract symptoms script
        subprocess.run(
            ["python", "../NLP/extract_symptoms.py"],
            check=True,
        )
        # Run the extract patient info script
        subprocess.run(
            ["python", "../NLP/extract_patient_info.py"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        return JSONResponse(status_code=500, content={"error": f"Pipeline failed:\n{error_output}"})

    patient_info_path = os.path.join(TRANSCRIPTS_DIR, "patient_info.json")

    if os.path.exists(patient_info_path):
        with open(patient_info_path, "r", encoding="utf-8") as f:
            patient_info_json = json.load(f)
    else:
        patient_info_json = {}

    return JSONResponse(content={"patient_info": patient_info_json})


@app.get("/patient-info")
async def get_patient_info():
    patient_info_path = os.path.join(TRANSCRIPTS_DIR, "patient_info.json")
    if os.path.exists(patient_info_path):
        with open(patient_info_path, "r", encoding="utf-8") as f:
            patient_info_json = json.load(f)
        return JSONResponse(content={"patient_info": patient_info_json})
    else:
        return JSONResponse(status_code=404, content={"error": "Patient info not found"})


# Mount frontend directory statically at root URL
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")