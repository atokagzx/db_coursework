import streamlit as st
import requests
import os
from config import backend_url, cc, get_session, redirect_to_login


st.title("Course Management System")
# redirect to login page if not logged in
if not get_session():
    redirect_to_login()
else:
    st.write("You are logged in as:")
    response = get_session().get(f"{backend_url}/auth/verify")
    if response.status_code == 200:
        data = response.json()
        st.markdown(f"**Username**: {data['user']['username']} id: {data['user']['user_id']}")
        st.write("You have the following roles:")
        for role in data['user']['roles']:
            st.markdown(f"**{role}**")
        
    else:
        st.write("Failed to verify login")
        redirect_to_login()