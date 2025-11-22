# tests/test_ingestion_bdd.py

import os
import pytest
from pytest_bdd import scenarios, given, when, then

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.document import Document
from app.models.user import User

# Link to the feature file (relative to tests/ folder)
scenarios("features/documagic_ingestion.feature")


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@given('the PostgreSQL database is running')
def db_running():
    """Basic check that DB session can be created."""
    db = SessionLocal()
    db.close()


@given('the "documents" and "users" tables exist')
def tables_exist():
    """Tables are created by app.main on startup, so we just assume they exist."""
    pass


@given('a user with id 1 exists as the system owner')
def system_user_exists():
    """Ensure there is a user with id=1 in the users table."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(
                id=1,
                email="system@documagic.local",
                password_hash="dummy-hash",
                full_name="System User",
            )
            db.add(user)
            db.commit()
    finally:
        db.close()


@given('the IMAP inbox "documagic_charity_society@zohomail.in" is reachable')
def inbox_reachable():
    """
    For now we rely on manual verification that Zoho IMAP is reachable.
    This is mainly a documentation step.
    """
    pass


@given('there are unread emails in the charity inbox with PDF attachments')
def unread_emails_exist():
    """
    Manual precondition: ensure at least one unread email with PDF
    attachment is present in the INBOX before running this test.
    """
    pass


@when('the ingestion API "/ingest/run" is called', target_fixture="ingestion_response")
def call_ingestion(client):
    """Call the ingestion endpoint and return the response."""
    response = client.post("/ingest/run")
    return response


@then('the API should respond with status 200')
def api_status_ok(ingestion_response):
    assert ingestion_response.status_code == 200


@then('the response should contain "processed_count" greater than or equal to 1')
def processed_count_ok(ingestion_response):
    data = ingestion_response.json()
    assert "processed_count" in data
    assert data["processed_count"] >= 1


@then('each processed item should include "uid", "subject", "from", and "attachments"')
def items_have_fields(ingestion_response):
    data = ingestion_response.json()
    for item in data.get("items", []):
        assert "uid" in item
        assert "subject" in item
        assert "from" in item
        assert "attachments" in item


@then('each attachment path from the response should correspond to a file on disk')
def attachments_exist_on_disk(ingestion_response):
    data = ingestion_response.json()
    for item in data.get("items", []):
        for path in item.get("attachments", []):
            assert os.path.isfile(path)


@then('for each saved attachment a new row should exist in the "documents" table')
def documents_exist_in_db(ingestion_response):
    data = ingestion_response.json()
    attachment_paths = []
    for item in data.get("items", []):
        attachment_paths.extend(item.get("attachments", []))

    # If no attachments were processed, we skip this assert
    if not attachment_paths:
        pytest.skip("No attachments processed, skipping DB document check")

    db = SessionLocal()
    try:
        docs = (
            db.query(Document)
            .filter(Document.file_path.in_(attachment_paths))
            .all()
        )
        assert len(docs) == len(attachment_paths)
    finally:
        db.close()
