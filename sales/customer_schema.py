from datetime import date
from pydantic import BaseModel


class CustomerBase(BaseModel):
    name: str
    cellphone: str
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    create_at: date | None = None
    update_at: date | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    cellphone: str | None = None
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    create_at: str | None = None
    update_at: str | None = None


class Customer(CustomerBase):
    id: int

    class Config:
        orm_mode = True
