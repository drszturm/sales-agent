import logging
from typing import Any
from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.database.database import engine, get_db
from sales.customer_model import Base
from sales.customer_schema import Customer, CustomerCreate
from sales.customer_model import Customer
from sales.customers_service import CustomerService

Base.metadata.create_all(bind=engine)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerManager:
    def __init__(self):
        db_gen = get_db()
        self.db: Session = next(db_gen)

    def create_customer(self, customer: CustomerCreate, db: Session = Depends(get_db)):
        try:
            service = CustomerService(self.db)
            return service.create_customer(customer)
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise

    def get_customer(self, cellphone: str, db: Session = Depends(get_db)):
        try:
            logger.info(f"Getting customer with cellphone: {cellphone}")
            service = CustomerService(self.db)
            customer = service.get_customer(cellphone)
            logger.info(f"Retrieved customer: {customer}")
            return customer

            if customer is None:
                logger.info("Customer not found")
            return customer
        except Exception as e:
            logger.error(f"Error retrieving customer: {e}")
            raise

    async def get_customers(self, skip: int = 0, limit: int = 100) -> Any:
        return self.db.query(Customer).offset(skip).limit(limit).all()
