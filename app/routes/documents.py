from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_documents():
    return {"message": "Documents router working"}
