import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from sales.customer_model import Customer
from sales.customer_schema import CustomerCreate, CustomerUpdate
from shared.metrics import instrument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, cellphone: str) -> Any:
        return self.db.query(Customer).filter(Customer.cellphone == cellphone).first()

    @instrument
    def get_customer_by_id(self, id: int) -> Any:
        return self.db.query(Customer).filter(Customer.id == id).first()

    @instrument
    def get_customers(self, skip: int = 0, limit: int = 100) -> Any:
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def create_customer(self, customer: CustomerCreate) -> Customer:
        db_customer = Customer(
            name=customer.name,
            cellphone=customer.cellphone,
            email=customer.email,
            address=customer.address,
            notes=customer.notes,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )
        logger.info(f"Creating customer: {db_customer}{self.db}")
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    @instrument
    def update_customer(
        self, customer_id: str, customer: CustomerUpdate
    ) -> Customer | None:
        db_customer = self.get_customer(customer_id)
        if db_customer:
            update_data = customer.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_customer, field, value)
            self.db.commit()
            self.db.refresh(db_customer)
        return db_customer

    @instrument
    def delete_customer(self, customer_id: str) -> bool:
        db_customer = self.get_customer(customer_id)
        if db_customer:
            self.db.delete(db_customer)
            self.db.commit()
            return True
        return False

    @instrument
    def update_customer_address(self, phone: str, address: str) -> Customer | None:
        db_customer = self.get_customer(phone)
        if db_customer:
            setattr(db_customer, "address", address)
            self.db.commit()
            self.db.refresh(db_customer)
        return db_customer
