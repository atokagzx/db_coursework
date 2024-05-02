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
    