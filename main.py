from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import models
from database import engine 
from routers import tasks, users 

models.Base.metadata.create_all(bind=engine)# create tables

app = FastAPI(
    title="Navas Task Manager API",
    description="A simple task manager built with FastAPI and SQLite",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # React dev server
        "http://localhost:5173",    # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f" {request.method} {request.url}")
    response = await call_next(request)
    duration = time.time() - start_time 
    print(f" {response.status_code} completed in {duration:.3f}s")
    return response 


app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Welcome to Navas Task Manager API"}