from pydantic import BaseModel, Field
from typing import Annotated, Optional
from fastapi import Query
from datetime import *

class UserCreate(BaseModel):
    username: Annotated[str, Query(min_length=3, max_length=20, pattern="^[a-zA-Z0-9@._-]+$")]
    password: Annotated[str | None, Query(min_length=3, max_length=50)]
    mail: Annotated[str, Query(pattern=r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$')] = None
class UserRoleUpdate(BaseModel):
    user_id: int
    new_role: str
class MedicationsCreate(BaseModel):
    name: str
    description: str | None
    prescription: bool
class DrugPrescriptionCreate(BaseModel):
    patient_id: int
    pharmacy_id: int 
    medication_id: int
    instruction: str | None
    quantity: int
    end_date: datetime
class PcharmaciesCreate(BaseModel):
    name: str
    address: str
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class DrugPrescriptionDetailResponse(BaseModel):
    id: int
    patient_username: str   
    pharmacy_name: str      
    medication_name: str   
    instruction: Optional[str] = None
    quantity: int           
    end_date: Optional[datetime] = None 

    model_config = ConfigDict(from_attributes=True)
class SupportMessege(BaseModel):
    messege: str