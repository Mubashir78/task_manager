from pydantic import BaseModel
from typing import Optional, List

class TaskBase(BaseModel):
    title: str 
    description: Optional[str] = None 

class TaskCreate(TaskBase):
    owner_id: int 

class TaskUpdate(BaseModel):
    title: Optional[str] = None 
    description: Optional[str] = None 
    completed: Optional[bool] = None 

class TaskResponse(TaskBase):
    id: int 
    completed: bool 
    owner_id: int 

    class Config:
        from_attributes = True 

class UserBase(BaseModel):
    name: str 
    email: str 

class UserCreate(UserBase):
    pass 

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(UserBase):
    id: int 
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True 