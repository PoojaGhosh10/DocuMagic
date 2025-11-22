# app/routes/__init__.py

from .auth import router as auth_router
from .users import router as users_router
from .documents import router as documents_router
from .ingest import router as ingest_router

__all__ = ["auth_router", "users_router", "documents_router", "ingest_router"]
