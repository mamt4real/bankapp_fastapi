from .. import models, schemas, utils
from fastapi import APIRouter,  status, HTTPException, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List
from ..oauth2 import restrict_access_to, get_current_user, check_current_user

router = APIRouter(
    prefix="/api/customers", tags=["Customers"]
)


@router.get("", response_model=List[schemas.Customer])
async def get_all_customers(db: Session = Depends(get_db), user=Depends(restrict_access_to("admin"))):
    customers = db.query(models.Customer).all()
    return customers


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Customer)
async def create_customer(new_user: schemas.CustomerCreate, db: Session = Depends(get_db), user=Depends(restrict_access_to("admin"))):
    user = new_user.dict()
    user["password"] = utils.hash(user["password"])
    data = models.Customer(**user)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@router.get("/me", response_model=schemas.Customer)
async def getMe(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return user


@router.put("/me", response_model=schemas.Customer)
async def updateMe(
    data: schemas.CustomerUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    Customer = models.Customer
    data = data.dict()
    utils.cleanNulls(data)
    if data == {}:
        return user
    db.query(Customer).where(Customer.customer_id ==
                             user.customer_id).update(data)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{cusID}", response_model=schemas.Customer)
async def get_user(cusID: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(
        models.Customer.customer_id == cusID).first()

    if not customer:
        raise HTTPException(
            status_code=404, detail=f"customer with id={cusID} not found!")

    return customer
