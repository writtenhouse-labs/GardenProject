import requests
import streamlit as st

from api_client import post
from ui import configure_page, initialize_session, portal_card, render_footer, render_heading, render_nav


configure_page("Login", "corn.png")
initialize_session()
render_nav()

with portal_card():
    if st.session_state["logged_in"]:
        render_heading("corn.png", "Employee Login", "You are already logged in.")
        if st.session_state.get("auth_message"):
            st.info(st.session_state.pop("auth_message"))
        st.markdown("[Open Profile](/Profile)")
    else:
        render_heading("corn.png", "Employee Login", "Log in to access your Employee Portal account.")

        with st.form("login-form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            try:
                result = post("/auth/login", {"email": email, "password": password})
            except requests.RequestException as exc:
                st.error(f"Could not reach the API: {exc}")
            else:
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.session_state["user_role"] = "applicant"
                st.session_state["auth_message"] = result["message"]
                st.rerun()

        st.caption("Not a member yet? Use the Register page.")

render_footer()
