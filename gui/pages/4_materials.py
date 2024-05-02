import streamlit as st
import requests
import os
import base64
import logging
import json
from config import backend_url, cc, get_session, redirect_to_login


def save_material(material_id, content):
    session = get_session()
    response = session.patch(f"{backend_url}/material/{material_id}", data={"content": content})
    if response.status_code == 200:
        st.success("Материал успешно обновлен!")
    else:
        st.error(f"Ошибка при создании материала: {response.json()}")

def show_materials(module_id):
    session = get_session()
    response = session.get(f"{backend_url}/material/{module_id}")
    if response.status_code == 200:
        data = response.json()
        st.markdown(f"### Материалы")
        for material in data:
            st.markdown(f"**Material ID**: {material['material_id']}")
            st.markdown(f"**Content Type**: {material['content_type']}")
            content = json.loads(material['content'])
            if content is not None:
                if material['content_type'] == "base64png":
                    try:
                        st.image(base64.b64decode(material['content']))
                    except Exception as e:
                        st.error(f"Ошибка при загрузке изображения: {e}")
                elif material['content_type'] == "markdown":
                    st.markdown(content)
            if st.button(f"Удалить материал", key=f"delete_{material['material_id']}"):
                response = session.delete(f"{backend_url}/material/{material['material_id']}")
                if response.status_code == 200:
                    st.success("Материал успешно удален!")
                    st.rerun()
                else:
                    st.error(f"Ошибка при удалении: {response.json()}")
            # add button to edit material
            if material['content_type'] == "base64png":
                uploaded_file = st.file_uploader("Загрузить новое изображение", type=["png", "jpg", "jpeg"], key=f"upload_image_{material['material_id']}")
                if uploaded_file is not None:
                    logging.info(f"Updating image: {uploaded_file.name}")
                    m = base64.b64encode(uploaded_file.read()).decode()
                    st.button("Сохранить изменения", key=f"save_image_{material['material_id']}", on_click=save_material, args=(material['material_id'], m))
            elif material['content_type'] == "markdown":
                new_content = st.text_area("Редактировать текст (markdown)", value=content)
                st.button("Сохранить изменения", key=f"save_markdown_{material['material_id']}", on_click=save_material, args=(material['material_id'], new_content))
            else:
                logging.error("Unknown content type")
                st.error("Неизвестный тип контента")
            st.markdown(f"---")
    else:
        st.error("Ошибка при загрузке материалов")
        st.json(response.json())

if get_session() is None:
    redirect_to_login()
else:
    # show dropdown to select course
    session = get_session()
    courses_response = session.get(f"{backend_url}/courses/created_by_me")
    if courses_response.status_code == 200:
        data = courses_response.json()
        course_id = st.selectbox("Выбрать курс", (f"{course['course_id']}: {course['course_name']}" for course in data))
        course_id = course_id.split(":")[0]
    else:
        st.error("Failed to fetch courses")
        st.json(courses_response.json())
        st.stop()
    # show dropdown to select module
    modules_response = session.get(f"{backend_url}/modules/{course_id}")
    if modules_response.status_code == 200:
        data = modules_response.json()
        module_id = st.selectbox("Выбрать модуль", (f"{module['module_id']}: {module['module_name']}" for module in data))
        if module_id is None:
            st.error("Данный курс не содержит модулей")
            st.stop()
        module_id = module_id.split(":")[0]
    else:
        st.error("Failed to fetch modules")
        st.json(modules_response.json())
        st.stop()
    # show materials
    show_materials(module_id)
    # create new material
    st.markdown(f"### Создать новый материал")
    content_type = st.selectbox("Тип контента", ["base64png", "markdown"])
    if st.button("Создать материал"):
        session = get_session()
        session.post(f"{backend_url}/material/{module_id}", params={"content_type": content_type})
        st.success("Материал успешно создан!")
        st.rerun()
        