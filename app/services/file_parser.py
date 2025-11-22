# app/services/file_parser.py

import os
from typing import Dict

# Optional PDF parsing
try:
    from PyPDF2 import PdfReader
    _HAS_PYPDF2 = True
except Exception:
    _HAS_PYPDF2 = False


def parse_file(file_path: str) -> Dict:
    """
    Returns basic metadata about a file.

    Always safe even if:
      - the file does not exist, or
      - PDF parsing fails.

    Returned keys:
      - filename      : basename of the file
      - file_path     : absolute path
      - size_bytes    : size in bytes, or None if unavailable
      - file_type     : extension without the dot (e.g. 'pdf', 'txt')
      - pages         : int for PDFs, or None for others / failure
    """
    info: Dict = {}

    # filename & absolute path
    info["filename"] = os.path.basename(file_path)
    info["file_path"] = os.path.abspath(file_path)

    # file size
    try:
        info["size_bytes"] = os.path.getsize(file_path)
    except Exception:
        info["size_bytes"] = None

    # file extension
    _, ext = os.path.splitext(file_path)
    info["file_type"] = ext.lower().lstrip(".")

    # default page count
    info["pages"] = None

    # parse pdf pages if possible
    if _HAS_PYPDF2 and info["file_type"] == "pdf":
        try:
            reader = PdfReader(file_path)
            info["pages"] = len(reader.pages)
        except Exception:
            info["pages"] = None

    return info
