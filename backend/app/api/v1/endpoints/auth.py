from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db, get_current_user
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.models.user import User
from backend.app.schemas.auth import Token, UserLogin, UserCreate, UserRead

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    access_token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login-json", response_model=Token)
def login_json(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.username)
    ).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        department=payload.department
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/seed-users")
def seed_default_users(db: Session = Depends(get_db)):
    """Seed standard SIH hackathon demonstration accounts."""
    default_users = [
        {
            "username": "admin",
            "email": "admin@landvault.gov.in",
            "password": "adminpassword123",
            "full_name": "Dr. Rameshwar Rao, IAS",
            "role": "admin",
            "department": "Directorate of Land Records & Survey"
        },
        {
            "username": "verifier",
            "email": "verifier@landvault.gov.in",
            "password": "verifierpassword123",
            "full_name": "Smt. Shailaja Sharma",
            "role": "verifier",
            "department": "Tahsildar & Revenue Verification Division"
        },
        {
            "username": "viewer",
            "email": "viewer@landvault.gov.in",
            "password": "viewerpassword123",
            "full_name": "Citizen / Bank Audit Officer",
            "role": "viewer",
            "department": "Public Registry & Legal Verification"
        }
    ]

    created = []
    for u in default_users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            new_u = User(
                username=u["username"],
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                department=u["department"]
            )
            db.add(new_u)
            created.append(u["username"])

    db.commit()
    return {"message": "Users initialized", "created": created}
