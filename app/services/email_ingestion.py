# app/services/email_ingestion.py

from dotenv import load_dotenv
load_dotenv()

import os
import ssl
import email
from datetime import datetime
from typing import List, Dict, Optional

from imapclient import IMAPClient
from dateutil import parser as date_parser

from app.config import settings
from app.database import SessionLocal
from app.models.document import Document
from app.services.file_parser import parse_file


# In-memory tracking of last processed UID for this app run
_last_uid: Optional[int] = None


def _ensure_storage_dir() -> str:
    """
    Ensure the charity society's document storage folder exists.
    Returns the absolute path.
    """
    base = settings.document_storage_path or "uploads"
    abs_path = os.path.abspath(base)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def _clean_filename(name: str) -> str:
    """
    Sanitize filenames so they are safe to store on disk.
    """
    return "".join(
        c for c in name if c.isalnum() or c in (" ", ".", "_", "-")
    ).strip()


def _save_attachment(part, uid: int) -> Optional[str]:
    """
    Save one attachment from the email into the uploads/ folder.
    Returns the absolute file path, or None if no filename / data.
    """
    filename = part.get_filename()
    if not filename:
        return None

    storage_dir = _ensure_storage_dir()
    filename = _clean_filename(filename)

    # prefix with UID + timestamp to avoid collisions
    prefix = f"{uid}_{int(datetime.utcnow().timestamp())}"
    safe_name = f"{prefix}_{filename}"
    dest_path = os.path.join(storage_dir, safe_name)

    payload = part.get_payload(decode=True)
    if not payload:
        return None

    with open(dest_path, "wb") as f:
        f.write(payload)

    return os.path.abspath(dest_path)


def _decode_envelope_field(field) -> str:
    """
    Safely decode IMAP envelope fields to string.
    """
    try:
        if isinstance(field, bytes):
            return field.decode(errors="ignore")
        return str(field or "")
    except Exception:
        return ""


def fetch_new_attachments(since_uid: Optional[int] = None) -> List[Dict]:
    """
    Low-level function:

    - Connects to the Zoho IMAP inbox of the charity society
    - Fetches either:
        * all UNSEEN messages (if since_uid is None), or
        * only newer messages (UID > since_uid)
    - Saves attachments to disk
    - Returns a list of dicts with email + attachment info:

      {
        "uid": int,
        "subject": str,
        "from": str,
        "date": str,
        "attachments": [<absolute paths>]
      }
    """
    host = settings.email_host
    port = int(settings.email_port or 993)
    user = settings.email_user
    password = settings.email_password

    ctx = ssl.create_default_context()
    results: List[Dict] = []

    with IMAPClient(host, port=port, ssl=True, ssl_context=ctx) as client:
        client.login(user, password)
        client.select_folder("INBOX")

        # search criteria
        if since_uid:
            criteria = ["UID", f"{since_uid + 1}:*"]
        else:
            criteria = ["UNSEEN"]

        uids = list(client.search(criteria))
        if not uids:
            return results

        data = client.fetch(uids, ["RFC822", "ENVELOPE", "UID"])

        for uid, item in data.items():
            raw_msg = item.get(b"RFC822")
            if not raw_msg:
                continue

            msg = email.message_from_bytes(raw_msg)
            env = item.get(b"ENVELOPE")

            subject = ""
            sender = ""
            date_val = ""

            if env:
                # subject
                try:
                    subject = _decode_envelope_field(getattr(env, "subject", ""))
                except Exception:
                    subject = ""

                # from: mailbox@host
                try:
                    if getattr(env, "from_", None):
                        f = env.from_[0]
                        mailbox = _decode_envelope_field(getattr(f, "mailbox", b""))
                        host_part = _decode_envelope_field(getattr(f, "host", b""))
                        if mailbox and host_part:
                            sender = f"{mailbox}@{host_part}"
                        else:
                            sender = _decode_envelope_field(f)
                except Exception:
                    sender = ""

                # date
                try:
                    date_val = getattr(env, "date", "") or ""
                except Exception:
                    date_val = ""

            saved_paths: List[str] = []

            if msg.is_multipart():
                for part in msg.walk():
                    cd = (part.get("Content-Disposition") or "").lower()
                    if "attachment" in cd:
                        saved = _save_attachment(part, int(uid))
                        if saved:
                            saved_paths.append(saved)

            if saved_paths:
                results.append(
                    {
                        "uid": int(uid),
                        "subject": subject,
                        "from": sender,
                        "date": str(date_val),
                        "attachments": saved_paths,
                    }
                )

    return results


def process_email_batch() -> int:
    """
    High-level function for DocuMagic charity workflow:

    - Fetch new email attachments from the charity inbox.
    - For each attachment:
        * Save to disk (already done in fetch_new_attachments)
        * Parse basic metadata via file_parser.parse_file()
        * Insert a Document row in the DB (owner_id fixed for now, e.g., 1)
    - Track last UID so that repeated calls only handle new emails.

    Returns:
        int: number of Document rows created in this batch.
    """
    global _last_uid

    rows = fetch_new_attachments(since_uid=_last_uid)
    if not rows:
        return 0

    db = SessionLocal()
    count = 0
    max_uid_seen = _last_uid or 0

    try:
        for r in rows:
            # optional: parse received date (not stored in Document right now)
            parsed_date = None
            if r.get("date"):
                try:
                    parsed_date = date_parser.parse(r["date"])
                except Exception:
                    parsed_date = None

            for path in r.get("attachments", []):
                # Use file_parser to get metadata like filename, size, pages etc.
                meta = parse_file(path)

                try:
                    doc = Document(
                        filename=meta.get("filename") or os.path.basename(path),
                        file_path=meta.get("file_path") or os.path.abspath(path),
                        owner_id=1,  # For charity society, treat 1 as system/admin owner
                    )
                    db.add(doc)
                    count += 1
                except Exception:
                    # Skip problematic attachments but continue others
                    continue

            # update max UID seen
            try:
                uid_val = int(r.get("uid") or 0)
                if uid_val > max_uid_seen:
                    max_uid_seen = uid_val
            except Exception:
                pass

        db.commit()

        if max_uid_seen > (_last_uid or 0):
            _last_uid = max_uid_seen

        return count
    finally:
        db.close()


def fetch_and_process_unread_emails() -> List[Dict]:
    """
    Backwards-compatible helper:

    - Processes a batch (saving Documents into DB)
    - Returns the raw rows with metadata, so /ingest/run can show something.

    Use this in your FastAPI route if you want a JSON response to show
    what was ingested from the charity society inbox.
    """
    global _last_uid

    rows = fetch_new_attachments(since_uid=_last_uid)
    if not rows:
        return []

    db = SessionLocal()
    max_uid_seen = _last_uid or 0

    try:
        for r in rows:
            for path in r.get("attachments", []):
                meta = parse_file(path)
                try:
                    doc = Document(
                        filename=meta.get("filename") or os.path.basename(path),
                        file_path=meta.get("file_path") or os.path.abspath(path),
                        owner_id=1,
                    )
                    db.add(doc)
                except Exception:
                    continue

            try:
                uid_val = int(r.get("uid") or 0)
                if uid_val > max_uid_seen:
                    max_uid_seen = uid_val
            except Exception:
                pass

        db.commit()

        if max_uid_seen > (_last_uid or 0):
            _last_uid = max_uid_seen

        return rows
    finally:
        db.close()
