from pydantic import BaseModel, Field
from typing import Annotated
from fastapi import Query

class UserCreate(BaseModel):
    username: Annotated[str, Query(min_length=3, max_length=20, pattern="^[a-zA-Z0-9@._-]+$")] = None
    password: Annotated[str | None, Query(min_length=3, max_length=50)] = None
    mail: Annotated[str, Query(pattern=r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$')] = None
class UserRoleUpdate(BaseModel):
    user_id: int
    new_role: str
class MedicationsCreate(BaseModel):
    name: str
    description: str | None
    prescription_required: bool