# app/config.py

import os
from dotenv import load_dotenv

# Base directory of the project (folder that contains app/ and .env)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Load .env if present (but don't fail if missing)
load_dotenv(ENV_PATH)


class Settings:
    """
    Simple settings loader for DocuMagic Charitable Society.

    - Tries to read from .env
    - If a value is missing, uses safe defaults you already provided
      so the app always has something to run with.
    """

    def __init__(self) -> None:
        # Database
        self.database_url = os.getenv(
            "database_url",
            "postgresql://docuuser:DocuMagic123@localhost:5432/documagicdb",
        )

        # Email / IMAP settings
        self.email_host = os.getenv("email_host", "imap.zoho.in")
        self.email_port = int(os.getenv("email_port", "993"))
        self.email_user = os.getenv(
            "email_user",
            "documagic_charity_society@zohomail.in",
        )
        self.email_password = os.getenv(
            "email_password",
            "DocuMagic123",
        )

        # Document storage path
        self.document_storage_path = os.getenv("document_storage_path", "uploads")


# Single global settings instance used everywhere
settings = Settings()
