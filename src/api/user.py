from fastapi import Depends, HTTPException, Query, APIRouter, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, update
from pydantic import Field, ValidationError
import re

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
        "username": current_user.username
    }
@router.get("/home")
def return_all_user():
    with Session(engine) as session:
        stmt = select(func.count(users.User.id))
        count = session.execute(stmt).scalar()
    
    return {"total_users": count}

from datetime import datetime, timezone
# ... остальные импорты ...

@router.get("/home/my_prescriptions", response_model=list[DrugPrescriptionDetailResponse])
def get_my_active_prescriptions(
    db: Session = Depends(get_db),
    current_user: users.User = Depends(get_current_user) # Функция получения текущего юзера из токена
):
    current_time = datetime.now(timezone.utc)

    # Строим запрос с JOIN, как делали в предыдущем шаге
# В твоем FastAPI роуте замени .join на .outerjoin
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
        #.filter(users.Prescription.patient_id == current_user.id)
        # ФИЛЬТРУЕМ активные рецепты (где end_date больше текущего времени или пустая)
        #.filter(
        #    (users.Prescription.end_date > current_time) | 
        #    (users.Prescription.end_date == None)
        #)
        .all()
    )
        
    return prescriptions
