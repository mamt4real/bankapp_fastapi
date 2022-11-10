from fastapi import APIRouter,  status, HTTPException, Depends, Response
from ..database import get_db
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"], prefix="/api")


@router.post("/login", response_model=schemas.Token)
async def login(res: Response, login_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Customer).filter(
        models.Customer.customer_email == login_details.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    if not utils.verify(login_details.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Credentials")

    # create token
    token = oauth2.create_access_token(data={"user_id": user.customer_id})
    res.set_cookie(key="token", value=token)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(res: Response, new_customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    try:
        customer = new_customer.dict()
        customer["password"] = utils.hash(customer["password"])
        customer = models.Customer(**customer)
        db.add(customer)
        db.commit()
        db.refresh(customer)
        token = oauth2.create_access_token(
            data={"user_id": customer.customer_id})
        res.set_cookie(key="token", value=token)
        return {"data": customer, "access_token": token, "token_type": "bearer"}
    except Exception as ex:
        raise HTTPException(
            status_code=400, detail=ex.args[0]
        )


@router.put("/update-password", response_model=schemas.Token)
async def updateMyPassword(
    res: Response, data: schemas.PasswordUpdate,
    db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)
):
    if not data.password == data.confirmpass:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Password Mismatch")
    if not utils.verify(data.oldpass, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Credentials")
    db.query(models.Customer).where(
        models.Customer.customer_id == user.customer_id
    ).update({"password": utils.hash(data.password)})
    db.commit()
    token = oauth2.create_access_token(
        data={"user_id": user.customer_id})
    res.set_cookie(key="token", value=token)
    return {"message": "Password Updated successfully", "access_token": token, "token_type": "bearer"}
