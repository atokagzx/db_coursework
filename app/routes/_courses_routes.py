import alchemy_contrib as am  # alchemy models
from sqlalchemy import exc as sqlalchemy_exc
import psycopg2

from fastapi import APIRouter, Depends, HTTPException, status
import pydantic_contrib as pm  # pydantic models

from configure import *
import typing

router = APIRouter()


@router.post("/courses", response_model=pm.CourseFull, tags=["courses"])
def create_course(course: pm.CourseBase,
                  user: dict = UserDependency,
                  db_session = Depends(DBFacade().db_session)):
    '''
    Create a course.
    '''
    # check if user is an admin
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can create courses")
    new_course = am.Course(course_name=course.course_name,
                            description=course.description,
                            created_by=user["user_id"],
                            created_at=am.datetime.utcnow())
    db_session.add(new_course)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db_session.refresh(new_course)
    return pm.CourseFull(course_id=new_course.course_id,
                         course_name=new_course.course_name,
                         description=new_course.description,
                         created_by=new_course.created_by,
                         created_at=new_course.created_at)


@router.get("/courses", response_model=typing.List[pm.CourseFull], tags=["courses"])
def get_courses(user: dict = UserDependency, db_session = Depends(DBFacade().db_session)):
    '''
    Get all courses.
    '''
    courses = db_session.query(am.Course).all()
    return [pm.CourseFull(course_id=course.course_id,
                          course_name=course.course_name,
                          description=course.description,
                          created_by=course.created_by,
                          created_at=course.created_at) for course in courses]


@router.get("/courses/created_by_me", response_model=typing.List[pm.CourseFull], tags=["courses"])
def get_courses_created_by_me(user: dict = UserDependency, db_session = Depends(DBFacade().db_session)):
    '''
    Get all courses created by the user.
    '''
    courses = db_session.query(am.Course).filter(am.Course.created_by == user["user_id"]).all()
    return [pm.CourseFull(course_id=course.course_id,
                          course_name=course.course_name,
                          description=course.description,
                          created_by=course.created_by,
                          created_at=course.created_at) for course in courses]


@router.post("/courses/{course_id}/students", response_model=typing.List[pm.UserBase], tags=["courses"])
def add_user_to_course(course_id: int,
                      user_id: int,
                    user: dict = UserDependency,
                      db_session = Depends(DBFacade().db_session)):
    '''
    Add a user to a course.
    '''
    course = db_session.query(am.Course).filter(am.Course.course_id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator of the course can add users to it")
    user_to_add = db_session.query(am.User).filter(am.User.user_id == user_id).first()
    if user_to_add is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # get student role id
    role = db_session.query(am.Role).filter(am.Role.role_name == "student").first()
    # check if  user has student role
    user_role = db_session.query(am.UserRole).filter(am.UserRole.user_id == user_id,
                                                        am.UserRole.role_id == role.role_id).first()
    if user_role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a student")
    registration = db_session.query(am.CourseRegistration).filter(am.CourseRegistration.course_id == course_id,
                                                                 am.CourseRegistration.user_id == user_id).first()
    if registration is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered for this course")
    new_registration = am.CourseRegistration(course_id=course_id, user_id=user_id)
    db_session.add(new_registration)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db_session.refresh(new_registration)
    return [pm.UserBase(user_id=user_to_add.user_id,
                        username=user_to_add.username,
                        email=user_to_add.email,
                        created_at=user_to_add.created_at)]


@router.get("/courses/{course_id}/students", response_model=typing.List[pm.UserBase], tags=["courses"])
def get_students_in_course(course_id: int,
                           user: dict = UserDependency,
                           db_session = Depends(DBFacade().db_session)):
    '''
    Get all students in a course.
    '''
    course = db_session.query(am.Course).filter(am.Course.course_id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator of the course can view students")
    registers = db_session.query(am.CourseRegistration).filter(am.CourseRegistration.course_id == course_id).all()
    students = []
    for register in registers:
        student = db_session.query(am.User).filter(am.User.user_id == register.user_id).first()
        students.append(pm.UserBase(user_id=student.user_id,
                                    username=student.username,
                                    email=student.email))
    return students
       

@router.delete("/courses/{course_id}", tags=["courses"])
def delete_course(course_id: int,
                  user: dict = UserDependency,
                  db_session = Depends(DBFacade().db_session)):
    '''
    Delete a course.
    '''
    course = db_session.query(am.Course).filter(am.Course.course_id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator of the course can delete it")
    # delete in cascade
    db_session.delete(course)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.exception(e) 
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Failed to delete course: {str(e)}')
    return {"message": "Course deleted successfully!"}