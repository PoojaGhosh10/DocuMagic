# app/routes/ingest.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.services.email_ingestion import fetch_and_process_unread_emails

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/run", summary="Run email ingestion now")
def run_ingestion():
    try:
        processed = fetch_and_process_unread_emails()
        return {"processed_count": len(processed), "items": processed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
def test_ingest():
    return {"message": "Ingest router working"}
