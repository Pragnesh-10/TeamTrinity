from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uuid
from orchestrator import start_pipeline, get_job_status, get_job

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "model": "ollama-llama3"}

import os

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    os.makedirs("/tmp/mf-xray", exist_ok=True)
    file_path = f"/tmp/mf-xray/{job_id}.pdf"
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    start_pipeline(job_id, is_demo=False, file_path=file_path)
    return {"job_id": job_id}

@app.post("/api/demo")
def trigger_demo():
    job_id = str(uuid.uuid4())
    start_pipeline(job_id, is_demo=True)
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    return get_job_status(job_id)

@app.get("/api/result/{job_id}")
def get_result(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found"}
    return job.get("result", {})
