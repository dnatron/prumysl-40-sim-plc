"""
Databázové připojení a session management
"""

from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL

# Vytvoření engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """Vytvoří databázi a tabulky"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency pro získání databázové session"""
    with Session(engine) as session:
        yield session
