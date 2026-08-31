from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database import models


DATABASE_URL = "sqlite:///equipes.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base.metadata.create_all(bind=engine)

print("Banco de dados criado com sucesso!")
