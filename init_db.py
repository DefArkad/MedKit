from src.config.database.db_config import engine, Base
from src.models import users # Важно импортировать модели, чтобы Base о них узнал

print("Создаю базу данных...")
# Эта команда создает все таблицы, которые описаны в моделях
Base.metadata.create_all(bind=engine)
print("Готово! Проверь проводник в VS Code.")