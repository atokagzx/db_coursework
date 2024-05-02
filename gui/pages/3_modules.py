import streamlit as st
import requests
import os
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
            # add button to delete module
            if st.button(f"Удалить модуль", key=f"delete_{module['module_id']}"):
                response = session.delete(f"{backend_url}/courses/{course_id}/modules/{module['module_id']}")
                if response.status_code == 200:
                    st.success("Модуль успешно удален!")
                    st.rerun()
                else:
                    st.error(f"Ошибка при удалении: {response.json()}")
            st.markdown(f"---")
    else:
        st.error("Ошибка при загрузке модулей")
        st.json(response.json())


def create_modules(course_id):
    session = get_session()
    def delete_module(module_id):
        response = session.delete(f"{backend_url}/courses/{course_id}/modules/{module_id}")
        if response.status_code == 200:
            st.success("Модуль успешно удален!")
        else:
            st.error(f"Ошибка при удалении: {response.json()}")
    response = session.get(f"{backend_url}/courses/{course_id}/modules")
    if response.status_code == 200:
        data = response.json()
        # show as markdown
        st.markdown(f"### Modules in course {course_id}")
        for module in data:
            st.markdown(f"**Module Name**: {module['module_name']}")
            st.markdown(f"**Description**: {module['description']}")
            st.markdown(f"**Created at**: {module['created_at']}")
            st.markdown(f"**Module ID**: {module['module_id']}")
            if st.button(f"Delete", on_click=delete_module, args=(module['module_id'],), key=module['module_id']):
                st.write(f"Deleting {module['module_name']}...")
            st.markdown(f"---")
    st.markdown(f"### Создать новый модуль")
    # Form to input module details
    module_name = st.text_input("Имя модуля")
    description = st.text_area("Описание модуля")
    
    # Button to submit module creation
    if st.button("Создать модуль"):
        module_data = {
            "module_name": module_name,
            "module_description": description,
            "course_id": course_id,
        }
        response = session.post(f"{backend_url}/modules", json=module_data)
        if response.status_code == 200:
            st.success("Модуль успешно создан!")
            st.rerun()
        else:
            st.error(f"Ошибка при создании модуля: {response.json()}")



if get_session() is None:
    redirect_to_login()
else:
    # show dropdown to select course
    session = get_session()
    response = session.get(f"{backend_url}/courses/created_by_me")
    if response.status_code == 200:
        data = response.json()
        course_id = st.selectbox("Выбрать курс", (f"{course['course_id']}: {course['course_name']}" for course in data))
        course_id = course_id.split(":")[0]
    else:
        st.error("Failed to fetch courses")
        st.json(response.json())
        st.stop()
        
    show_modules(course_id)
    create_modules(course_id)