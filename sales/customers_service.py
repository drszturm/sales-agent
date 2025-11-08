
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from sqlalchemy.orm import Session


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def get_customer(self, customer_id: int) -> Customer | None:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_customers(self, skip: int = 0, limit: int = 100) -> list[Customer]:
        return self.db.query(Customer).offset(skip).limit(limit).all()

    def create_customer(self, customer: CustomerCreate) -> Customer:
        db_customer = Customer(
            name=customer.name,
            cellphone=customer.cellphone,
            email=customer.email,
            address=customer.address,
            notes=customer.notes,
        )
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def update_customer(
        self, customer_id: int, customer: CustomerUpdate
    ) -> Customer | None:
        db_customer = self.get_customer(customer_id)
        if db_customer:
            update_data = customer.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_customer, field, value)
            self.db.commit()
            self.db.refresh(db_customer)
        return db_customer

    def delete_customer(self, customer_id: int) -> bool:
        db_customer = self.get_customer(customer_id)
        if db_customer:
            self.db.delete(db_customer)
            self.db.commit()
            return True
        return False
