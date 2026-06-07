from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./peptides.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    url = Column(String, nullable=False)
    weight_mg = Column(Float, nullable=False)
    price_per_mg = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return Session(engine)
