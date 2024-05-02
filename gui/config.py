from streamlit_cookies_controller import CookieController
import os
import requests
import streamlit as st
import logging

# create requests session at login page
backend_url = f'http://{os.getenv("BACKEND_HOST")}:{os.getenv("BACKEND_PORT")}'
cc = CookieController()
logging.basicConfig(level=logging.INFO)

streamlit_root_logger = logging.getLogger(st.__name__)
streamlit_root_logger.setLevel(logging.INFO)

def get_session():
    token = cc.get("auth_token")
    logging.info(f"token: {token}")
    if not token:
        return None
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session


def redirect_to_login():
    st.write("Вы не вошли, пожалуйста, войдите")
    st.write("Click [here](/login) to login")
    st.stop()

    