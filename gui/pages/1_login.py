import streamlit as st
import requests
import os
from config import backend_url, cc, get_session

def on_logout_click():
    cc.remove("auth_token")
    st.session_state.session = None
    st.write("вы вышли")


def on_check_login_status_click():
    session = get_session()
    response = session.get(f"{backend_url}/auth/verify")
    if response.status_code == 200:
        st.write("Вы вошли как:")
        st.write(response.json())
    else:
        cc.remove("auth_token")
        st.write("Вы не вошли")

def get_session():
    token = cc.get("auth_token")
    # if token is missing, goto login page
    if not token:
        return None
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session


def login():
    if get_session():
        st.write("Вы вошли")
        st.button("Check login status", on_click=on_check_login_status_click)
        st.button("Выйти", on_click=on_logout_click)
        
    def on_login_click():
        response = requests.post(f'{backend_url}/token',
                                data={"grant_type": "",
                                      "username": username,
                                      "password": password,
                                      "scope": "",
                                      "client_id": "",
                                      "client_secret": ""})
        if response.status_code == 200:
            cc.set("auth_token", response.json()["access_token"])
            st.session_state.session = get_session()
        else:
            st.write("Login failed")

    st.write(cc.get("auth_token"))
    st.title("Вход в систему")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    st.button("Войти", on_click=on_login_click)
# render login page
login()