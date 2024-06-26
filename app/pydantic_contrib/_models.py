from typing import List, Literal, Optional, Union, Tuple
from pydantic import BaseModel
from datetime import datetime, date


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    expires_at: datetime


class DefaultMessage(BaseModel):
    message: str


class Verify(DefaultMessage):
    user: dict


class UserBase(BaseModel):
    user_id: int
    username: str
    email: str


class UserFull(UserBase):
    created_at: datetime
    roles: List[str]


class CourseBase(BaseModel):
    course_name: str
    description: str


class CourseFull(CourseBase):
    course_id: int
    created_by: int
    created_at: datetime
    

class ModuleBase(BaseModel):
    module_name: str
    module_description: str
    course_id: int


class ModuleFull(ModuleBase):
    module_id: int


class AssignmentBase(BaseModel):
    assignment_description: str
    due_date: date
    module_id: int


class AssignmentFull(AssignmentBase):
    assignment_id: int

MaterialContentType = Literal['base64png', 'markdown']

class MaterialFull(BaseModel):
    material_id: int
    module_id: int
    content_type: MaterialContentType
    content: Optional[str]
    url: str
    

class TestBase(BaseModel):
    module_id: int
    test_description: str


class TestFull(TestBase):
    test_id: int


class QuestionBase(BaseModel):
    question_text: str
    correct_answer: str


class QuestionFull(QuestionBase):
    test_id: int
    question_id: int


class AnswerBase(BaseModel):
    question_id: int
    given_answer: str


class AnswerFull(AnswerBase):
    answer_id: int
    is_correct: bool


class CreateTestTask(BaseModel):
    test: TestBase
    questions: List[QuestionBase]

class QuestionWithoutAnswer(BaseModel):
    question_text: str
    question_id: int

class GetTestTask(BaseModel):
    test: TestFull
    questions: List[QuestionWithoutAnswer]
