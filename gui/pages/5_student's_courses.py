import streamlit as st
import requests
import os
import base64
import logging
import json
from config import backend_url, cc, get_session, redirect_to_login

def show_materials(module_id):
    session = get_session()
    response = session.get(f"{backend_url}/material/{module_id}")
    if response.status_code == 200:
        data = response.json()
        st.markdown(f"### Материалы")
        for material in data:
            content = json.loads(material['content'])
            if content is not None:
                if material['content_type'] == "base64png":
                    try:
                        st.image(base64.b64decode(material['content']))
                    except Exception as e:
                        st.error(f"Ошибка при загрузке изображения: {e}")
                elif material['content_type'] == "markdown":
                    st.markdown(content)
                st.markdown(f"---")
    else:
        st.error("Ошибка при загрузке материалов")
        st.json(response.json())

def show_tests(module_id):
    session = get_session()
    response = session.get(f"{backend_url}/test/{module_id}")
    if response.status_code == 200:
        data = response.json()
        st.markdown(f"### Тесты")
        for test in data:
            st.markdown(f"#### {test['test']['test_description']}")
            for question in test['questions']:
                st.markdown(f"##### {question['question_text']}")
                # add answer input
                given_answer = st.text_input("Ответ")
                if st.button("Ответить"):
                    answer = {"question_id": question['question_id'], "given_answer": given_answer}
                    response = session.post(f"{backend_url}/test/{question['question_id']}/answer", params={"question_id": question['question_id']}, json=answer)
                    if response.status_code == 200:
                        result = response.json()["message"].strip().lower()
                        if "incorrect" in result:
                            st.error(result)
                        else:
                            st.success(result)
                    else:
                        st.error(response.json())
            st.markdown(f"---")
    else:
        st.error("Ошибка при загрузке тестов")
        st.json(response.json())

if get_session() is None:
    redirect_to_login()
else:
    # show dropdown to select course
    session = get_session()
    courses_response = session.get(f"{backend_url}/courses/my_courses")
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
    show_tests(module_id)