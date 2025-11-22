from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserOut, Login, Token
from app.utils import hash_password, verify_password
from app.auth import create_access_token
from app.dependencies import get_current_user   # <-- REQUIRED

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================
# REGISTER NEW USER
# ============================
@router.post("/register", response_model=UserOut)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================
# LOGIN USER
# ============================
@router.post("/login", response_model=Token)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": str(user.id)})

    # Important: include token_type so Swagger Authorize works
    return {"access_token": token, "token_type": "bearer"}


# ============================
# PROTECTED ROUTE — CURRENT USER
# ============================
@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
