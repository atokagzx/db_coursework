import streamlit as st
import requests
import os
import logging
from config import backend_url, cc, get_session, redirect_to_login


def show_modules(course_id):
    session = get_session()
    response = session.get(f"{backend_url}/modules/{course_id}")
    if response.status_code == 200:
        data = response.json()
        st.markdown(f"### Модули")
        for module in data:
            st.markdown(f"**Имя модуля**: {module['module_name']}")
            st.markdown(f"**Описание**: {module['module_description']}")
            st.markdown(f"**Module ID**: {module['module_id']}")
            st.markdown(f"---")
    else:
        st.error("Ошибка при загрузке модулей")
        st.json(response.json())


def show_students(course_id):
    session = get_session()
    response = session.get(f"{backend_url}/courses/{course_id}/students")
    if response.status_code == 200:
        data = response.json()
        st.markdown(f"### Зарегистрированные студенты")
        for student in data:
            st.markdown(f"**Имя**: {student['username']} id: {student['user_id']} email: {student['email']}")
            st.markdown(f"---")
    all_students = session.get(f"{backend_url}/users/students")
    if all_students.status_code == 200:
        data = all_students.json()
        # filter out students already in the course
        st.markdown(f"### Добавить студента")
        logging.info(data)
        data = [student for student in data if student['user_id'] not in [student['user_id'] for student in response.json()]]
        student = st.selectbox("Выберите студента", options=[f"{student['user_id']}: {student['username']}" for student in data], key=f"select_student_{course_id}")
        if student is not None:
            student_id = student.split(":")[0]
            if st.button("Добавить"):
                response = session.post(f"{backend_url}/courses/{course_id}/students", data={"user_id": student_id})
                if response.status_code == 200:
                    st.success("Студент успешно добавлен!")
                    st.rerun()
                else:
                    st.error("Ошибка при добавлении студента")
                    st.json(response.json())
    else:
        st.error("Ошибка при загрузке студентов")
        st.json(response.json())



def create_course():
    # show existing courses
    session = get_session()
    def delete_course(course_id):
        response = session.delete(f"{backend_url}/courses/{course_id}")
        if response.status_code == 200:
            st.success("Курс успешно удален!")
        else:
            st.error(f"Ошибка при удалении: {response.json()}")
    response = session.get(f"{backend_url}/courses/created_by_me")
    if response.status_code == 200:
        data = response.json()
        # show as markdown
        st.markdown(f"### Курсы, созданные вами")
        for course in data:
            st.markdown(f"**Имя курса**: {course['course_name']}")
            st.markdown(f"**Описание**: {course['description']}")
            st.markdown(f"**Created at**: {course['created_at']}")
            st.markdown(f"**Course ID**: {course['course_id']}")
            if st.button(f"Удалить", on_click=delete_course, args=(course['course_id'],), key=f"delete_{course['course_id']}"):
                st.write(f"Deleting {course['course_name']}...")
            show_modules(course['course_id'])
            show_students(course['course_id'])
            
            st.markdown(f"---")
    st.markdown(f"### Создать новый курс")
    # Form to input course details
    course_name = st.text_input("Имя курса")
    description = st.text_area("Описание курса")
    
    # Button to submit course creation
    if st.button("Create Course"):
        course_data = {
            "course_name": course_name,
            "description": description,
        }

        # API call to create a course
        response = session.post(f"{backend_url}/courses", json=course_data)
        
        if response.status_code == 200:
            st.success("Курс успешно создан!")
            st.json(response.json())
            st.rerun()
        else:
            st.error("Ошибка при создании курса")
            st.json(response.json())

if get_session() is None:
    redirect_to_login()
else:
    create_course()