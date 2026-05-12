from fastapi import Depends, HTTPException, status
from typing import Annotated
import jwt
from src.config.database.db_config import get_db, SECRET_KEY, ALGORITHM, oauth2_scheme
from src.models import users
from sqlalchemy.orm import Session
from transliterate import translit
from src.schemas.user import UserCreate


db_dep = Annotated[Session, Depends(get_db)]
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dep):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Не удалось подтвердить личность",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Расшифровываем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        # Если токен подделан, просрочен или поврежден
        raise credentials_exception

    # 2. Ищем пользователя в базе данных
    user = db.query(users.User).filter(users.User.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user # Возвращаем полноценный объект пользователя из БД

class RoleChecker:
    def __init__(self, need_role: str):
        self.need_role = need_role

    def __call__(self, current_user: Annotated[users.User, Depends(get_current_user)]):

        if current_user.role != self.need_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="У вас недостаточно прав"
            )
        return current_user
    
def generate_username(user_data: UserCreate):
    return translit(user_data.username, language_code='ru', reversed=False)

