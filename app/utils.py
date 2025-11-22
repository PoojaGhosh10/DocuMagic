from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BCRYPT_BYTE_LIMIT = 72

def _truncate_password_to_72_bytes(password: str) -> str:
    """
    Truncate the password to at most 72 bytes (UTF-8). Return a string
    decoded from those bytes (may cut multi-byte char at the end).
    """
    if password is None:
        return ""
    b = password.encode("utf-8", errors="ignore")
    if len(b) <= BCRYPT_BYTE_LIMIT:
        return password
    truncated = b[:BCRYPT_BYTE_LIMIT].decode("utf-8", errors="ignore")
    return truncated

def hash_password(password: str) -> str:
    safe_pw = _truncate_password_to_72_bytes(password)
    return pwd_context.hash(safe_pw)

def verify_password(plain_password: str, hashed: str) -> bool:
    safe_pw = _truncate_password_to_72_bytes(plain_password)
    return pwd_context.verify(safe_pw, hashed)
