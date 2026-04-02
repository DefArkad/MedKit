from fastapi import Depends, HTTPException, Query, APIRouter

from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from dotenv import load_dotenv

from src.config.database.db_config import get_db, engine, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, pwd_context, oauth2_scheme
from src.models import users



db_dep = Annotated[Session, Depends(get_db)]


router = APIRouter()

load_dotenv()
def create_access_token(data: dict):
    to_encode = data.copy()
    # Используем время с учетом часового пояса (timezone.utc)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Генерируем токен через PyJWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class UserCreate(BaseModel):
    username: Annotated[str, Query(min_length=3, max_length=20, pattern="^[a-zA-Z0-9_-]+$")] = None
    password: Annotated[str | None, Query(min_length=3, max_length=50)] = None,


@router.post("/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(users.User).filter(users.User.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_pwd = pwd_context.hash(user_data.password)

    new_user = users.User(username=user_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Пользователь успешно создан", "user_id": new_user.id}

@router.post("/login")
def login_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Ищем пользователя по имени
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