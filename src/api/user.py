from fastapi import Depends, HTTPException, Query, APIRouter, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func, update
from pydantic import Field, ValidationError
import re

from src.models import users
from src.config.database.db_config import get_db, pwd_context, engine
from src.models import users
from src.schemas.user import UserCreate, UserRoleUpdate
from src.core.token import create_access_token
from src.dependencies import get_current_user, RoleChecker

db_dep = Annotated[Session, Depends(get_db)]

router = APIRouter()


@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(users.User).filter(users.User.username == user_data.username).first() and db.query(users.User).filter(users.User.mail == user_data.mail).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    

    hashed_pwd = pwd_context.hash(user_data.password)

    new_user = users.User(username=user_data.username, mail = user_data.mail, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Пользователь успешно создан", "user_id": new_user.id}

@router.post("/login")
def login_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Ищем пользователя по имени
    #email_pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    
    if re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', user_data.username):
        user = db.query(users.User).filter(users.User.mail == user_data.username).first()
    else:
        user = db.query(users.User).filter(users.User.username == user_data.username).first()

    
    # 2. Если пользователя нет
    if not user:
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    # 3. Проверяем пароль (сравниваем хеши через нашу pbkdf2_sha256)
    if not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    # 4. Если всё ок — создаем токен
    access_token = create_access_token(data={"sub": user.username})

    # 5. Возвращаем токен фронтенду
    return {"access_token": access_token, "token_type": "bearer"}



# Убедись, что тут написано именно /users/me (со всеми слэшами)
@router.get("/users/me") 
def read_users_me(current_user: Annotated[users.User, Depends(get_current_user)]):
    return {
        "id": current_user.id, 
        "username": current_user.username
    }
@router.get("/home")
def return_all_user():
    with Session(engine) as session:
        stmt = select(func.count(users.User.id))
        count = session.execute(stmt).scalar()
        
    return {"total_users": count}

