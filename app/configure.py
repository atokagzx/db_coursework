# Standard imports
import os
import logging
from functools import partial

# Database imports
from alchemy_contrib import DBFacade
import alchemy_contrib._models as am

# MongoDB imports
from mongo_contrib import MongoFacade


# Authentication and Authorization imports
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError

from fastapi import FastAPI, Depends, HTTPException, status

import datetime

tags_metadata = [
]


logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] (%(name)s:%(funcName)s): %(message)s")
SECRET_KEY_FILE = os.environ.get("SECRET_KEY_FILE")
ALGORITHM = os.environ.get("SIGN_ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", default="30"))

with open(SECRET_KEY_FILE, 'r') as f:
    SECRET_KEY = f.read().strip()
    if not SECRET_KEY:
        raise ValueError("secret key file is empty")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger('app')
_db_facade = DBFacade()
_mongo_facade = MongoFacade()


# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        iat: int = payload.get("iat")
        exp: int = payload.get("exp")
        issued_at = datetime.datetime.fromtimestamp(iat)
        expires_at = datetime.datetime.fromtimestamp(exp)
        # check if user exists
        user, roles = DBFacade().get_user(username)
        if not user or user.user_id != user_id:
            # if user does not exist, raise an exception at the end of the function
            logger.info(f'user "{username}" with uid "{user_id}" not found')
        else:
            return {"username": username, "user_id": user_id, "roles": roles}
    except jwt.ExpiredSignatureError as e:
        logger.info(f"token's signature has expired: {e}")
    except PyJWTError as e:
        logger.exception(f'error during token verification')
    raise credentials_exception


UserDependency = Depends(get_current_user)


HTTPConflictException = partial(HTTPException, 
                            status_code=status.HTTP_409_CONFLICT, 
                            headers={"WWW-Authenticate": "Bearer"})


HTTPNotFoundException = partial(HTTPException,
                            status_code=status.HTTP_404_NOT_FOUND,
                            headers={"WWW-Authenticate": "Bearer"})

HTTPInternalServerError = partial(HTTPException,
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            headers={"WWW-Authenticate": "Bearer"})
