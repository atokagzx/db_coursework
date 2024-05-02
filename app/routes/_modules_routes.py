import alchemy_contrib as am  # alchemy models
from sqlalchemy import exc as sqlalchemy_exc

from fastapi import APIRouter, Depends, HTTPException, status
import pydantic_contrib as pm  # pydantic models

from configure import *
import typing

router = APIRouter()


@router.post("/modules", response_model=pm.ModuleFull, tags=["modules"])
def create_module(module: pm.ModuleBase,
                  user: dict = UserDependency,
                  db_session = Depends(DBFacade().db_session)):
    '''
    Create a module.
    '''
    # check if user is an admin
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can create modules")
    # check if course exists
    course = db_session.query(am.Course).filter(am.Course.course_id == module.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    # check if course is created by the user
    if course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and course creators can create modules")
    new_module = am.Module(module_name=module.module_name,
                            module_description=module.module_description,
                            course_id=module.course_id)
    db_session.add(new_module)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db_session.refresh(new_module)
    return pm.ModuleFull(module_id=new_module.module_id,
                         module_name=new_module.module_name,
                         module_description=new_module.module_description,
                            course_id=new_module.course_id,
    )

@router.get("/modules/{course_id}", response_model=typing.List[pm.ModuleFull], tags=["modules"])
def get_modules(course_id: int,
                user: dict = UserDependency,
                db_session = Depends(DBFacade().db_session)):
    '''
    Get all modules for a course.
    '''
    modules = db_session.query(am.Module).filter(am.Module.course_id == course_id).all()
    return [pm.ModuleFull(module_id=module.module_id,
                          module_name=module.module_name,
                          module_description=module.module_description,
                          course_id=module.course_id) for module in modules]

