import alchemy_contrib as am  # alchemy models
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy import Text

from fastapi import APIRouter, Depends, HTTPException, status
import pydantic_contrib as pm  # pydantic models

from configure import *
import typing

router = APIRouter()

@router.get("/users/students", response_model=typing.List[pm.UserFull], tags=["users"])
def get_students(user: dict = UserDependency,
                 db_session = Depends(DBFacade().db_session)):
    '''
    Get all students.
    '''
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can view students")
    role = db_session.query(am.Role).filter(am.Role.role_name == "student").first()
    students = db_session.query(am.UserRole).filter(am.UserRole.role_id == role.role_id).all()
    return [pm.UserFull(user_id=student.user_id,
                        username=student.user.username,
                        email=student.user.email,
                        created_at=student.user.created_at,
                        roles=[role.role_name]) for student in students]


@router.get("/users/instructors", response_model=typing.List[pm.UserFull], tags=["users"])
def get_instructors(user: dict = UserDependency,
                    db_session = Depends(DBFacade().db_session)):
    '''
    Get all instructors.
    '''
    if "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view instructors")
    role = db_session.query(am.Role).filter(am.Role.role_name == "instructor").first()
    instructors = db_session.query(am.UserRole).filter(am.UserRole.role_id == role.role_id).all()
    return [pm.UserFull(user_id=instructor.user_id,
                        username=instructor.user.username,
                        email=instructor.user.email,
                        created_at=instructor.user.created_at,
                        roles=[role.role_name]) for instructor in instructors]
