# models.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Загрузить .env из UTF-8 без BOM
load_dotenv()

# 2. Прочитать параметры пула транзакций
DB_USER     = os.getenv("DB_USER")      # postgres.fvcbuhnbqlqlmtxuixas
DB_PASSWORD = os.getenv("DB_PASSWORD")  # ваш пароль
DB_HOST     = os.getenv("DB_HOST")      # aws-0-eu-central-1.pooler.supabase.com
DB_PORT     = os.getenv("DB_PORT")      # 6543
DB_NAME     = os.getenv("DB_NAME")      # postgres

# 3. Проверить, что ничего не пропущено
missing = [k for k,v in {
    "DB_USER":DB_USER, "DB_PASSWORD":DB_PASSWORD,
    "DB_HOST":DB_HOST, "DB_PORT":DB_PORT, "DB_NAME":DB_NAME
}.items() if not v]
if missing:
    raise RuntimeError(f"В .env не заданы: {', '.join(missing)}")

# 4. Собрать DSN с требованием SSL и опцией UTF-8
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?sslmode=require"
)

# 5. Создать движок с указанием кодировки
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"options": "-c client_encoding=utf8"}
)

# 6. Сессии и базовый класс
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# === Твои модели ===

class Teacher(Base):
    __tablename__ = "teachers"
    id         = Column(Integer, primary_key=True)
    name       = Column(String, nullable=False)
    position   = Column(String, nullable=False)
    experience = Column(String)
    photo      = Column(String)
    link       = Column(String)

class Event(Base):
    __tablename__ = "events"
    id          = Column(Integer, primary_key=True)
    title       = Column(String)
    description = Column(String)
    article     = Column(String)
    link        = Column(String)
    date        = Column(Date)
    image       = Column(String)

class EventImage(Base):
    __tablename__ = "event_images"
    id         = Column(Integer, primary_key=True)
    event_id   = Column(Integer, ForeignKey("events.id"))
    image_path = Column(String)

# 7. (Опционально) создаём таблицы
Base.metadata.create_all(bind=engine)
