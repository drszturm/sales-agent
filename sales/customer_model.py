from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cellphone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    create_at = Column(Date, nullable=False)
    update_at = Column(Date, nullable=True)
