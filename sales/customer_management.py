from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.database.database import engine, get_db
from sales.customer_model import Base
from sales.customer_schema import CustomerCreate
from sales.customers_service import CustomerService

Base.metadata.create_all(bind=engine)


class CustomerManager:
    def __init__(self):
        db_gen = get_db()
        self.db: Session = next(db_gen)

    def create_customer(self, customer: CustomerCreate, db: Session = Depends(get_db)):
        service = CustomerService(self.db)
        return service.create_customer(customer)

    def get_customer(self, cellphone: str, db: Session = Depends(get_db)):
        service = CustomerService(self.db)
        customer = service.get_customer(cellphone)
        if customer is None:
            print("Customer not found")
        return customer
