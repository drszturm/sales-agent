import logging
from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.database.database import engine, get_db
from sales.customer_model import Base
from sales.customer_schema import CustomerCreate
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
        service = CustomerService(self.db)
        return service.create_customer(customer)

    def get_customer(self, cellphone: str, db: Session = Depends(get_db)):
        service = CustomerService(self.db)
        logger.info(f"Fetching customer with cellphone: {cellphone}")
        customer = service.get_customer(cellphone)
        logger.info(f"Found customer: {customer}")
        if customer is None:
            logger.info("Customer not found")
        return customer
