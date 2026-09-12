from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db
from core.models import User
from uuid import uuid4
import json

router = APIRouter()

class UserCreateSchema(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str

class AuthResponseSchema(BaseModel):
    user_id: str
    username: str
    token: str

@router.post("/signup", response_model=AuthResponseSchema)
async def signup(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario (MVP simple)"""
    existing = db.query(User).filter(
        (User.email == user_data.email) |
        (User.username == user_data.username)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    user = User(
        id=uuid4(),
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash="dummy"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = json.dumps({"user_id": str(user.id)})

    return AuthResponseSchema(
        user_id=str(user.id),
        username=user.username,
        token=token
    )

@router.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login (MVP: email + dummy password)"""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = json.dumps({"user_id": str(user.id)})

    return AuthResponseSchema(
        user_id=str(user.id),
        username=user.username,
        token=token
    )

@router.get("/me")
async def get_me(
    token: str = None,
    db: Session = Depends(get_db)
):
    """Obtener datos del usuario actual"""
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    try:
        payload = json.loads(token)
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")
