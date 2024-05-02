from functools import partial
from fastapi import APIRouter, Depends, HTTPException, status
import pydantic_contrib as pm # pydantic models
from fastapi.param_functions import Form

from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from configure import *

router = APIRouter()

WrongCredentials = partial(HTTPException, 
                           status_code=status.HTTP_401_UNAUTHORIZED, 
                           detail="Incorrect username or password", 
                           headers={"WWW-Authenticate": "Bearer"})


@router.post("/token", response_model=pm.Token, tags=["auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = DBFacade().get_user(form_data.username)[0]
    if not user:
        logger.info(f'could not find user "{form_data.username}"')
        raise WrongCredentials()
    if not verify_password(form_data.password, user.password_hash):
        logger.info(f'incorrect password for user "{form_data.username}"')
        raise WrongCredentials()
    iat = datetime.datetime.now()
    exp = iat + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username,
                                                "user_id": user.user_id,
                                                "iat": iat,
                                                "exp": exp})
    user_id = user.user_id
    logger.info(f'generated token\n\t- user: "{user.username}"\n\t- uid: "{user.user_id}"\n\t- expires: "{exp}"')
    return pm.Token(access_token=access_token, token_type="bearer", user_id=user_id, expires_at=exp)


@router.get("/auth/verify", response_model=pm.Verify, tags=["auth"])
def verify_token(user: dict = UserDependency):
    logger.info(f'verified token for user "{user["username"]}" with uid "{user["user_id"]}"')
    return pm.Verify(message="OK", user=user)


@router.post("/auth/register", response_model=pm.DefaultMessage, tags=["auth"])
def register_user(username: str = Form(..., description="Username"),
                    password: str = Form(..., description="Password"),
                    roles: List[str] = Form([], description="Roles"),
                    email: str = Form(..., description="Email")):
    roles = roles[0].split(",") if roles else list()
    roles = [role.lower().strip() for role in roles]
    logger.info(f'registering user "{username}" with roles {roles}')
    if DBFacade().get_user(username)[0]:
        logger.info(f'user "{username}" already exists')
        raise HTTPConflictException(detail=f"User with username '{username}' already exists")
    hashed_password = pwd_context.hash(password)
    DBFacade().register_user(username, hashed_password, roles, email)
    user = DBFacade().get_user(username)[0]
    logger.info(f'registered user "{username}" with uid "{user.user_id}"')
    return pm.DefaultMessage(message="OK")
