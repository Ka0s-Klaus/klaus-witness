from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.models import User
import json

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Validar token y retornar usuario actual"""
    # Para MVP: simple token validation con user_id en claims
    try:
        token = credentials.credentials
        payload = json.loads(token) if token.startswith('{') else {"user_id": token}

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")
