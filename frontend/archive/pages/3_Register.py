import requests
import streamlit as st

from api_client import post
from ui import configure_page, initialize_session, portal_card, render_footer, render_heading, render_nav


configure_page("Register", "capsicum.png")
initialize_session()
render_nav()

with portal_card():
    if st.session_state["logged_in"]:
        render_heading("capsicum.png", "Employee Portal Registration", "You are already logged in.")
        if st.session_state.get("auth_message"):
            st.success(st.session_state.pop("auth_message"))
        st.markdown("[Open Profile](/Profile)")
        st.stop()

    render_heading("capsicum.png", "Employee Portal Registration", "Create your Garden Project employee portal account.")

    with st.form("registration-form"):
        left, right = st.columns(2)
        with left:
            first_name = st.text_input("First Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone", placeholder="555-1234")
        with right:
            last_name = st.text_input("Last Name")
            password = st.text_input("Password", type="password")
            role = st.radio(
                "Select your role:",
                ["employee", "applicant"],
                format_func=lambda value: "I am a Garden Project employee"
                if value == "employee"
                else "I want to apply to the Garden Project",
            )

        address = st.text_input("Address")
        salary = None
        ssn = None
        if role == "employee":
            employee_left, employee_right = st.columns(2)
            with employee_left:
                salary = st.number_input("Salary", min_value=0.0, step=1000.0)
            with employee_right:
                ssn = st.text_input("SSN", placeholder="123-45-6789")

        submitted = st.form_submit_button("Register")

    if submitted:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "address": address,
            "phone": phone,
            "role": role,
            "salary": salary,
            "ssn": ssn,
        }
        try:
            result = post("/users/register", payload)
        except requests.RequestException as exc:
            st.error(f"Could not reach the API: {exc}")
        else:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_role"] = role
            st.session_state["auth_message"] = result["message"]
            st.rerun()

render_footer()
