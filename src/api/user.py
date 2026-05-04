from fastapi import Depends, HTTPException, Query, APIRouter, status, Body
from typing import Annotated, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, update
from pydantic import Field, ValidationError
import re
from datetime import datetime, timezone

from src.models import users
from src.config.database.db_config import get_db, pwd_context, engine
from src.models import users
from src.schemas.user import UserCreate, UserRoleUpdate, DrugPrescriptionDetailResponse
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
        "username": current_user.username,
        "role": current_user.role
    }
@router.get("/home")
def return_all_user():
    with Session(engine) as session:
        stmt = select(func.count(users.User.id))
        count = session.execute(stmt).scalar()
    
    return {"total_users": count}

# ... остальные импорты ...

@router.get("/home/my_prescriptions", response_model=list[DrugPrescriptionDetailResponse])
def get_my_active_prescriptions(
    db: Session = Depends(get_db),
    current_user: users.User = Depends(get_current_user)
):
    # Используем простую дату без сложной логики поясов для проверки
    current_time = datetime.now() 

    prescriptions = (
        db.query(
            users.Prescription.id,
            users.User.username.label("patient_username"),
            users.Pharmacy.name.label("pharmacy_name"),
            users.Medication.name.label("medication_name"),
            users.Prescription.instruction,
            users.Prescription.quantity,
            users.Prescription.end_date
        )
        .outerjoin(users.User, users.Prescription.patient_id == users.User.id)
        .outerjoin(users.Pharmacy, users.Prescription.pharmacy_id == users.Pharmacy.id)
        .outerjoin(users.Medication, users.Prescription.medication_id == users.Medication.id)
        .filter(users.Prescription.patient_id == current_user.id)
        .filter(
            (users.Prescription.end_date >= current_time) | 
            (users.Prescription.end_date == None)
        )
        .all()
    )
    return prescriptions
from pydantic import BaseModel

# Добавь эту схему туда, где у тебя остальные (или прямо перед роутом)
class ChatMessageCreate(BaseModel):
    text: str
    target_user_id: int | None = None

@router.post("/home/chat/send")
def send_message(
    msg: ChatMessageCreate, # Используем чистую и надежную схему
    db: Session = Depends(get_db),
    current_user: users.User = Depends(get_current_user)
):
    # Если пишет админ и указал ID, отправляем туда. Иначе - в свой чат.
    chat_owner_id = msg.target_user_id if current_user.role == "Admin" else current_user.id
    
    new_msg = users.SupportMessage(
        user_id=chat_owner_id,
        sender_id=current_user.id,
        message=msg.text
    )
    db.add(new_msg)
    db.commit()
    return {"status": "sent"}

@router.get("/home/chat/history/{user_id}")
def get_chat_history(
    user_id: int, 
    db: Session = Depends(get_db),
    # 1. Меняем RoleChecker на get_current_user, чтобы пускать всех авторизованных
    current_user: users.User = Depends(get_current_user) 
):
    # 2. Проверяем права: разрешаем доступ, если это Админ ИЛИ если пользователь запрашивает свой личный чат
    if current_user.role != "Admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к чужому чату")
        
    # 3. Получаем сообщения из базы данных
    messages = db.query(users.SupportMessage).filter(users.SupportMessage.user_id == user_id).all()
    
    # 4. Превращаем объекты SQLAlchemy в обычный список словарей, чтобы избежать ошибки 500 при отправке JSON
    return [{"sender_id": m.sender_id, "message": m.message} for m in messages]

