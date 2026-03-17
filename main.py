from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from summarizer import summarize_logs


app = FastAPI(title="LLM Log Summarizer")

class LogRequest(BaseModel):
    logs: str

class SummaryResponse(BaseModel):
    severity: str
    summary: str
    root_cause: str
    affected_services: list[str]
    resolved: bool

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/summarize", response_model=SummaryResponse)
def summarize(request: LogRequest):
    if not request.logs.strip():
        raise HTTPException(status_code=400, detail="Logs cannot be empty")
    result = summarize_logs(request.logs)
    return result