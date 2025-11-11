from customer_model import Base
from customer_schema import Customer, CustomerCreate, CustomerUpdate
from customer_service import CustomerService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from infrastructure.database.database import engine, get_db

# Create tables
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.create_customer(customer)


@router.get("/", response_model=list[Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = CustomerService(db)
    return service.get_customers(skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    service = CustomerService(db)
    customer = service.get_customer_by_id(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)
):
    service = CustomerService(db)
    db_customer = service.update_customer(customer_id, customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    service = CustomerService(db)
    success = service.delete_customer(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return None
