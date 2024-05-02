from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    create_engine,
    BigInteger,
    ARRAY,
    Sequence,
)
from sqlalchemy.orm import relationship, declarative_base, validates
from sqlalchemy.sql import func
from sqlalchemy import event, DDL
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import backref
from datetime import datetime


BaseDB = declarative_base()

"""

Table user {
  user_id integer [primary key, not null]
  username varchar [not null]
  password_hash varchar [not null]
  email varchar [not null]
  created_at timestamp [not null]
}

Table role {
  role_id integer [primary key, not null]
  role_name varchar [not null]
}

Table user_roles {
  user_id integer [ref: > user.user_id, not null]
  role_id integer [ref: > role.role_id, not null]
}

Table course {
  course_id integer [primary key, not null]
  course_name varchar [not null]
  description varchar [not null]
  created_by integer [ref: > user.user_id, not null]
  crated_at timestamp [not null]
}

Table module {
  module_id integer [primary key, not null]
  course_id integer [ref: > course.course_id, not null]
  module_name varchar [not null]
  module_description varchar [not null]
}

Table assignment{
  assignment_id integer [primary key, not null]
  module_id integer [ref: > module.module_id, not null]
  assignment_description varchar [not null]
  due_date timestamp [not null]
}

Table material {
  material_id integer [primary key, not null]
  module_id integer [ref: > module.module_id, not null]
  content_type varchar [not null]
  content text
  url varchar
}

Table submission {
  submission_id integer [primary key, not null]
  assignment_id integer [ref: > assignment.assignment_id, not null]
  user_id integer [ref: > user.user_id, not null]
  submission_date timestamp [not null]
  grade integer
}

Table test {
  test_id integer [primary key, not null]
  module_id integer [ref: > module.module_id, not null]
  test_description varchar [not null]
}

Table question {
  question_id integer [primary key, not null]
  test_id integer [ref: > test.test_id, not null]
  question_text text [not null]
  correct_answer varchar [not null]
}

Table user_answer {
  answer_id integer [primary key, not null]
  question_id integer [ref: > question.question_id, not null]
  user_id integer [ref: > user.user_id, not null]
  given_answer varchar [not null]
  is_correct boolean [not null]
}

Table course_registration {
  registration_id integer [primary key, not null]
  user_id integer [ref: > user.user_id, not null]
  course_id integer [ref: > course.course_id, not null]
  registration_date timestamp [not null]
}
"""

class User(BaseDB):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Role(BaseDB):
    __tablename__ = 'role'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String, nullable=False)

class UserRole(BaseDB):
    __tablename__ = 'user_roles'
    user_id = Column(Integer, ForeignKey('user.user_id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role.role_id'), primary_key=True)
    user = relationship("User", backref=backref("roles"))
    role = relationship("Role", backref=backref("users"))

class Course(BaseDB):
    __tablename__ = 'course'
    course_id = Column(Integer, primary_key=True)
    course_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    creator = relationship("User", backref="courses_created")

class Module(BaseDB):
    __tablename__ = 'module'
    module_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('course.course_id'), nullable=False)
    module_name = Column(String, nullable=False)
    module_description = Column(String, nullable=False)
    course = relationship("Course", backref="modules")

class Assignment(BaseDB):
    __tablename__ = 'assignment'
    assignment_id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('module.module_id'), nullable=False)
    assignment_description = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)

class Material(BaseDB):
    __tablename__ = 'material'
    material_id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('module.module_id'), nullable=False)
    content_type = Column(String, nullable=False)
    content = Column(Text)
    url = Column(String)
    module = relationship("Module", backref="materials")

class Submission(BaseDB):
    __tablename__ = 'submission'
    submission_id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey('assignment.assignment_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    submission_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    grade = Column(Integer)

class Test(BaseDB):
    __tablename__ = 'test'
    test_id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('module.module_id'), nullable=False)
    test_description = Column(String, nullable=False)

class Question(BaseDB):
    __tablename__ = 'question'
    question_id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('test.test_id'), nullable=False)
    question_text = Column(Text, nullable=False)
    correct_answer = Column(String, nullable=False)

class UserAnswer(BaseDB):
    __tablename__ = 'user_answer'
    answer_id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('question.question_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    given_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)

class CourseRegistration(BaseDB):
    __tablename__ = 'course_registration'
    registration_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('course.course_id'), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
