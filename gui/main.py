import streamlit as st
import requests
import os
from streamlit_cookies_controller import CookieController

# create requests session at login page
backend_url = f'http://{os.getenv("BACKEND_HOST")}:{os.getenv("BACKEND_PORT")}'
cc = CookieController()
def on_logout_click():
    cc.remove("auth_token")
    st.session_state.session = None
    st.session_state.logged_in = False
    st.write("You are logged out")
    st.button("Login", on_click=login)

def on_check_login_status_click():
    if st.session_state.logged_in:
        st.write("You are logged in")
    else:
        st.write("You are not logged in")
        st.button("Login", on_click=login)


def get_session():
    token = cc.get("auth_token")
    # if token is missing, goto login page
    if not token:
        return None
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})
    st.session_state.logged_in = True
    return session


def login():
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
        
        st.write("You are logged in")
        st.button("Check login status", on_click=on_check_login_status_click)
        st.button("Logout", on_click=on_logout_click)

    st.write(cc.get("auth_token"))
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    st.button("Login", on_click=on_login_click)
    
def create_course():
    # show existing courses
    session = get_session()
    def delete_course(course_id):
        response = session.delete(f"{backend_url}/courses/{course_id}")
        if response.status_code == 200:
            st.success("Course deleted successfully!")
        else:
            st.error(f"Failed to delete course: {response.json()}")
        st.rerun()
    response = session.get(f"{backend_url}/courses/created_by_me")
    if response.status_code == 200:
        data = response.json()
        # show as markdown
        st.markdown(f"### Courses created by you")
        for course in data:
            st.markdown(f"**Course Name**: {course['course_name']}")
            st.markdown(f"**Description**: {course['description']}")
            st.markdown(f"**Created at**: {course['created_at']}")
            st.markdown(f"**Course ID**: {course['course_id']}")
            st.link_button("Open course", f"/course/{course['course_id']}")
            if st.button(f"Delete", on_click=delete_course, args=(course['course_id'],), key=course['course_id']):
                st.write(f"Deleting {course['course_name']}...")
            st.markdown(f"---")
    st.markdown(f"### Create a new course")
    # Form to input course details
    course_name = st.text_input("Course Name")
    description = st.text_area("Course Description")
    
    # Button to submit course creation
    if st.button("Create Course"):
        course_data = {
            "course_name": course_name,
            "description": description,
        }

        # API call to create a course
        response = session.post(f"{backend_url}/courses", json=course_data)
        
        if response.status_code == 200:
            st.success("Course created successfully!")
            st.json(response.json())
            st.rerun()
        else:
            st.error("Failed to create course")
            st.json(response.json())


# on course open, show course details
        
page_names_to_funcs = {
    "Login": login,
    "Create Course": create_course,
}

st.session_state.logged_in = False
demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()