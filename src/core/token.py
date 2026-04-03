# src/api/security.py
import jwt
from datetime import datetime, timedelta, timezone
from src.config.database.db_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from dotenv import load_dotenv

load_dotenv()
def create_access_token(data: dict):
    to_encode = data.copy()
    # Используем время с учетом часового пояса (timezone.utc)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Генерируем токен через PyJWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt