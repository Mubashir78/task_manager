from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import crud, schemas
from database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    result = crud.create_task(db, task)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid owner_id or conflicting data")
    return result


@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=1000), completed: Optional[bool] = None, db: Session = Depends(get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit, completed=completed)


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = crud.update_task(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session =  Depends(get_db)):
    task = crud.delete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
