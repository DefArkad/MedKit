from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from src.config.database.db_config import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    mail = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="patient")
class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String) 
    prescription = Column(Boolean, default=False) 

class Pharmacy(Base):
    __tablename__ = "pharmacies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String) 

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Кто назначил, кому и где забирать
    doctor_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id"))
    medication_id = Column(Integer, ForeignKey("medications.id"))
    
    # Детали назначения
    instruction = Column(String)  # Как принимать (н-р, "2 раза в день")
    quantity = Column(Integer)    # Количество упаковок/таблеток
    
    # Статусы для Фармацевта и Врача
    is_issued = Column(Boolean, default=False) # Отметка фармацевта о выдаче
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    issued_at = Column(DateTime(timezone=True), nullable=True) # Когда выдано
    end_date = Column(DateTime(timezone=True))