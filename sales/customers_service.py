from datetime import datetime
import logging
from typing import Any

from sqlalchemy.orm import Session

from sales.customer_model import Customer
from sales.customer_schema import CustomerCreate, CustomerUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, cellphone: str) -> Any:
        return self.db.query(Customer).filter(Customer.cellphone == cellphone).first()

    def get_customer_by_id(self, id: int) -> Any:
        return self.db.query(Customer).filter(Customer.id == id).first()

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

    def delete_customer(self, customer_id: str) -> bool:
        db_customer = self.get_customer(customer_id)
        if db_customer:
            self.db.delete(db_customer)
            self.db.commit()
            return True
        return False
