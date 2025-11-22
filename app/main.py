# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# create app instance first
app = FastAPI(
    title="DocuMagic API",
    version="1.0.0",
    description=(
        "Backend for DocuMagic Charitable Society: "
        "email-based document ingestion, parsing, metadata extraction and storage."
    ),
)

# CORS setup (allows frontend like React/Vue to talk to API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # TODO: tighten this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# import route routers directly to avoid import-order problems
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.documents import router as documents_router
from app.routes.ingest import router as ingest_router

# register routers
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(documents_router, prefix="/documents", tags=["Documents"])
# Ingest router already has prefix="/ingest" and tags in the file itself
app.include_router(ingest_router)
# Auth router already has prefix="/auth"
app.include_router(auth_router)


# Root endpoint
@app.get("/")
def home():
    return {"message": "DocuMagic API is running..."}


# ensure DB tables exist on startup (imports models so metadata is registered)
from app.database import Base, engine
from app.models import user, document  # noqa: F401 (imported for side-effect)

Base.metadata.create_all(bind=engine)
