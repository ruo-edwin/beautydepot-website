import os

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlalchemy.orm import Session

from backend.db import get_db
from backend import models, schemas


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# JWT SETTINGS
# ============================================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY is not set in the .env file"
    )


ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


security = HTTPBearer()


# ============================================================
# GET CURRENT ADMIN
# ============================================================

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        admin_id = payload.get("sub")

        if admin_id is None:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )

    try:

        admin_id = int(admin_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    admin = db.query(models.Admin).filter(
        models.Admin.id == admin_id
    ).first()

    if not admin:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account not found"
        )

    if not admin.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    return admin


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=schemas.TokenResponse
)
def login(
    credentials: schemas.AdminLogin,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # FIND ADMIN
    # --------------------------------------------------------

    admin = db.query(models.Admin).filter(
        models.Admin.email == credentials.email
    ).first()

    if not admin:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # CHECK ACCOUNT STATUS
    # --------------------------------------------------------

    if not admin.is_active:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    # --------------------------------------------------------
    # VERIFY PASSWORD
    # --------------------------------------------------------

    if not pwd_context.verify(
        credentials.password,
        admin.password_hash
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # --------------------------------------------------------
    # CREATE TOKEN EXPIRATION
    # --------------------------------------------------------

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # --------------------------------------------------------
    # TOKEN DATA
    # --------------------------------------------------------

    token_data = {
        "sub": str(admin.id),
        "email": admin.email,
        "exp": expire
    }

    # --------------------------------------------------------
    # CREATE JWT
    # --------------------------------------------------------

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # --------------------------------------------------------
    # RETURN TOKEN
    # --------------------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }