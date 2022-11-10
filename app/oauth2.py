from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Cookie

from app import models
from app.config import settings
from .database import get_db
from sqlalchemy.orm import Session

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
JWT_EXPIRES_IN = settings.jwt_expires_in
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_IN)
    to_encode.update({"exp": expire, "iat": datetime.now()})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str, credentials_exception, raiseError=True):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            if raiseError:
                raise credentials_exception
            else:
                return None
        return id
    except JWTError:
        if raiseError:
            raise credentials_exception


def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    if not token:
        token = cookie_token
    id = verify_token(token, credentials_exception)
    user = db.query(models.Customer).filter(
        models.Customer.customer_id == id).first()
    return user


# Use for frontend cookie validation
# use in protected pages
def check_current_user(token: str = Cookie(None), db: Session = Depends(get_db)):
    if token is None:
        return None
    id = verify_token(token, None, False)
    if id is None:
        return None
    user = db.query(models.Customer).filter(
        models.Customer.customer_id == id).first()
    return user


def restrict_access_to(*roles: list):
    def inner_restrict(user=Depends(get_current_user)):
        if not user.clearance in roles:
            raise HTTPException(
                status_code=403, detail="Oops you are not cleared to perform this action"
            )
        return user
    return inner_restrict
