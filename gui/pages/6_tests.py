import streamlit as st
import requests
import os
import base64
import logging
import json
from config import backend_url, cc, get_session, redirect_to_login

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
    # create new material
    st.markdown(f"### Создать новый тест")
    test_description = st.text_input("Описание теста")
    questions = []
    qestion_count = 0
    while True:
        question_text = st.text_input("Текст вопроса", key=f"question_{qestion_count}").strip()
        correct_answer = st.text_input("Правильный ответ", key=f"correct_answer_{qestion_count}").strip()
        questions.append({"question_text": question_text, "correct_answer": correct_answer})
        qestion_count += 1
        if not st.button("Добавить еще вопрос", key=f"add_question_{qestion_count}"):
            break
    if st.button("Создать тест"):
        test = {"test": {"module_id": module_id, "test_description": test_description}, "questions": questions}
        response = session.post(f"{backend_url}/test", json=test)
        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(response.json())   
    # show tests