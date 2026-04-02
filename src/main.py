from fastapi import FastAPI
from src.api import main_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(main_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # Разрешаем запросы с любых адресов (для разработки)
    allow_credentials=True,
    allow_methods=["*"],             # Разрешаем все методы (GET, POST, OPTIONS и т.д.)
    allow_headers=["*"],             # Разрешаем любые заголовки
)