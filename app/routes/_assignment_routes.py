import alchemy_contrib as am  # alchemy models
from sqlalchemy import exc as sqlalchemy_exc

from fastapi import APIRouter, Depends, HTTPException, status
import pydantic_contrib as pm  # pydantic models

from configure import *
import typing

router = APIRouter()


@router.post("/assignments", response_model=pm.AssignmentFull, tags=["assignments"])
def create_assignment(assignment: pm.AssignmentBase,
                      user: dict = UserDependency,
                      db_session = Depends(DBFacade().db_session)):
    '''
    Create an assignment.
    '''
    # check if user is an admin
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can create assignments")
    # check if module exists
    module = db_session.query(am.Module).filter(am.Module.module_id == assignment.module_id).first()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    if module.course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and course creators can create assignments")
    new_assignment = am.Assignment(due_date=assignment.due_date,
                                    assignment_description=assignment.assignment_description,
                                    module_id=assignment.module_id)
    db_session.add(new_assignment)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db_session.refresh(new_assignment)
    return pm.AssignmentFull(assignment_id=new_assignment.assignment_id,
                             assignment_description=new_assignment.assignment_description,
                             module_id=new_assignment.module_id,
                                due_date=new_assignment.due_date)


@router.get("/assignments/{module_id}", response_model=typing.List[pm.AssignmentFull], tags=["assignments"])
def get_assignments(module_id: int,
                    user: dict = UserDependency,
                    db_session = Depends(DBFacade().db_session)):
    '''
    Get all assignments for a module.
    '''
    assignments = db_session.query(am.Assignment).filter(am.Assignment.module_id == module_id).all()
    return [pm.AssignmentFull(assignment_id=assignment.assignment_id,
                              assignment_description=assignment.assignment_description,
                              module_id=assignment.module_id,
                                due_date=assignment.due_date) for assignment in assignments]
