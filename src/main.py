from fastapi import FastAPI
from src.api import main_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(main_router)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null", # Это позволит делать запросы, даже если ты открыл файл просто из папки
]

# 2. Добавляем Middleware (ОБЯЗАТЕЛЬНО ДО include_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Разрешает все методы: GET, POST, OPTIONS и т.д.
    allow_headers=["*"], # Разрешает все заголовки
)


# 3. Монтируем фронтенд (как я советовал ранее)
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="frontend")