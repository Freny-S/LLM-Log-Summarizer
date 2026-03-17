from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from summarizer import summarize_logs
from chunker import chunk_logs_by_incident


app = FastAPI(title="LLM Log Summarizer")

class LogRequest(BaseModel):
    logs: str

class SummaryResponse(BaseModel):
    severity: str
    summary: str
    root_cause: str
    affected_services: list[str]
    resolved: bool

class BatchResponse(BaseModel):
    total_incidents: int
    incidents: list[SummaryResponse]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/summarize", response_model=SummaryResponse)
def summarize(request: LogRequest):
    if not request.logs.strip():
        raise HTTPException(status_code=400, detail="Logs cannot be empty")
    result = summarize_logs(request.logs)
    return result

@app.post("/upload", response_model=BatchResponse)
async def upload_log_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".log"):
        raise HTTPException(status_code=400, detail="Only .log files accepted")

    contents = await file.read()
    raw_logs = contents.decode("utf-8")

    chunks = chunk_logs_by_incident(raw_logs)
    if not chunks:
        raise HTTPException(status_code=400, detail="No log entries found in file")

    incidents = []
    for chunk in chunks:
        summary = summarize_logs(chunk)
        incidents.append(summary)

    return {
        "total_incidents": len(incidents),
        "incidents": incidents
    }