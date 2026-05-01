from fastapi import Depends, HTTPException, Query, APIRouter, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, func, update
from pydantic import Field, ValidationError
import re

from src.models import users
from src.config.database.db_config import get_db, pwd_context, engine
from src.schemas.user import UserCreate, UserRoleUpdate, MedicationsCreate, DrugPrescriptionCreate, PcharmaciesCreate
from src.core.token import create_access_token
from src.dependencies import get_current_user, RoleChecker

db_dep = Annotated[Session, Depends(get_db)]

router_staff = APIRouter()

# Теперь используем в роуте
@router_staff.get("/home/admin_panel")
def admin_panel(current_role: Annotated[users.User, Depends(RoleChecker(need_role="Admin"))]):
    return {
        "role": current_role.role
    }


@router_staff.get("/home/pharmacist_panel")
def pharmacist_panel(current_role: Annotated[users.User, Depends(RoleChecker(need_role="Pharmacist"))]):

    return {
        "role": current_role.role
    }


@router_staff.get("/home/doctor_panel")
def doctor_panel(current_role: Annotated[users.User, Depends(RoleChecker(need_role="Doctor"))]):
    return {
        "role": current_role.role
    }


@router_staff.patch("/home/change-role")
def change_user_role(
    role_data: UserRoleUpdate, 
    db: Session = Depends(get_db),
    # Только админ может изменять чужие роли
    current_admin: users.User = Depends(RoleChecker(need_role="Admin"))
):
    # 1. Ищем пользователя, роль которого хотим изменить
    target_user = db.query(users.User).filter(users.User.id == role_data.user_id).first()
    if not role_data.new_role in ["Admin", "patient", "Doctor", "Pharmacist"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Выберите коректную роль"
        )
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь с таким ID не найден"
        )

    # 2. Обновляем роль
    target_user.role = role_data.new_role
    
    # 3. Сохраняем изменения в БД
    db.commit()
    db.refresh(target_user)

    return {
        "message": f"Роль пользователя {target_user.username} успешно изменена на {target_user.role}",
        "updated_user_id": target_user.id
    }

@router_staff.post("/home/add-medications")
def add_medications(medications_data: MedicationsCreate, db: Session = Depends(get_db), current_role: users.User = Depends(RoleChecker(need_role="Doctor"))):
    new_medication = users.Medication(
        name=medications_data.name,
        description=medications_data.description,
        prescription=medications_data.prescription
    )
    
    db.add(new_medication)
    db.commit()
    db.refresh(new_medication)
    return {"message": "Лекарство добавлено", "id": new_medication.id}

@router_staff.post("/home/new_drug_prescription")
def add_drug_prescription(
    DataDrugPrescription: DrugPrescriptionCreate,
    db: Session= Depends(get_db),
    current_user: users.User = Depends(RoleChecker(need_role="Doctor"))
):
    target_user = db.query(users.User).filter(users.User.id == DataDrugPrescription.patient_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пользователь с таким username не найден"
        )
    new_drug_prescription = users.Prescription(patient_id=DataDrugPrescription.patient_id,doctor_id=current_user.id, pharmacy_id=DataDrugPrescription.pharmacy_id, medication_id=DataDrugPrescription.medication_id, instruction=DataDrugPrescription.instruction, quantity=DataDrugPrescription.quantity, end_date=DataDrugPrescription.end_date)
    db.add(new_drug_prescription)
    db.commit()
    db.refresh(new_drug_prescription)
    
@router_staff.post("/home/new_pharmacies")
def new_pharmacies(
    DataPcharmacies: PcharmaciesCreate,
    db: Session= Depends(get_db),
    current_user: users.User = Depends(RoleChecker(need_role="Admin"))
):
    new_pcharmacies = users.Pharmacy(name=DataPcharmacies.name, address=DataPcharmacies.address)
    db.add(new_pcharmacies)
    db.commit()
    db.refresh(new_pcharmacies)