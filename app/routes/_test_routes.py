import alchemy_contrib as am  # alchemy models
from sqlalchemy import exc as sqlalchemy_exc

from fastapi import APIRouter, Depends, HTTPException, status
import pydantic_contrib as pm  # pydantic models

from configure import *
import typing

router = APIRouter()


@router.post("/test", response_model=pm.DefaultMessage, tags=["test"])
async def create_test(test: pm.CreateTestTask, user: dict = UserDependency,
                db_session = Depends(DBFacade().db_session)):
    
    # check if user is an admin or instructor
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can create tests")
    module = test.test.module_id
    # check if module exists
    module = db_session.query(am.Module).filter(am.Module.module_id == module).first()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    if module.course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and course creators can create tests")
    new_test = am.Test(module_id=test.test.module_id, test_description=test.test.test_description)
    db_session.add(new_test)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db_session.refresh(new_test)
    test_id = new_test.test_id
    for question in test.questions:
        new_question = am.Question(test_id=test_id, question_text=question.question_text, correct_answer=question.correct_answer)
        db_session.add(new_question)
        try:
            db_session.commit()
        except sqlalchemy_exc.SQLAlchemyError as e:
            db_session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return pm.DefaultMessage(message="Test created successfully")


@router.get("/test/{module_id}", response_model=typing.List[pm.GetTestTask], tags=["test"])
def get_tests(module_id: int, user: dict = UserDependency,
                db_session = Depends(DBFacade().db_session)):
    '''
    Get all tests for a module.
    '''
    tests = db_session.query(am.Test).filter(am.Test.module_id == module_id).all()
    tests_response = []
    for test in tests:
        questions = db_session.query(am.Question).filter(am.Question.test_id == test.test_id).all()
        questions_response = [pm.QuestionWithoutAnswer(question_id=question.question_id, question_text=question.question_text) for question in questions]
        tests_response.append(pm.GetTestTask(test=pm.TestFull(test_id=test.test_id, module_id=test.module_id, test_description=test.test_description), questions=questions_response))
    return tests_response


@router.post("/test/{question_id}/answer", response_model=pm.DefaultMessage, tags=["test"])
async def answer_question(question_id: int, answer: pm.AnswerBase, user: dict = UserDependency,
                db_session = Depends(DBFacade().db_session)):
    '''
    Answer a question.
    '''
    question = db_session.query(am.Question).filter(am.Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    is_correct = question.correct_answer == answer.given_answer
    new_answer = am.UserAnswer(question_id=question_id, user_id=user["user_id"], given_answer=answer.given_answer, is_correct=is_correct)
    db_session.add(new_answer)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return pm.DefaultMessage(message="Correct answer" if is_correct else "Incorrect answer")
