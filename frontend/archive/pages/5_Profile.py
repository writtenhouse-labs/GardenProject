import requests
import streamlit as st

from api_client import get
from ui import configure_page, initialize_session, portal_card, render_footer, render_heading, render_nav


configure_page("Profile", "capsicum.png")
initialize_session()
render_nav()

with portal_card():
    render_heading("capsicum.png", "My Profile", "Profile fields mirror the employee portal layout.")

    if not st.session_state["logged_in"]:
        st.warning("Please log in to view your profile.")
        st.markdown("[Go to Login](/Login)")
        st.stop()

    email = st.text_input("Profile Email", value=st.session_state.get("user_email") or "sample@gardenproject.local")
    if st.button("Load Profile"):
        try:
            profile = get("/users/profile", {"email": email})
        except requests.RequestException as exc:
            st.error(f"Could not reach the API: {exc}")
        else:
            left, right = st.columns(2)
            with left:
                st.text_input("First Name", value=profile["first_name"], disabled=True)
                st.text_input("Email", value=profile["email"], disabled=True)
                st.text_input("Address", value=profile["address"], disabled=True)
                st.text_input("Salary", value=profile["salary"], disabled=True)
            with right:
                st.text_input("Last Name", value=profile["last_name"], disabled=True)
                st.text_input("Password", value="********", type="password", disabled=True)
                st.text_input("Phone", value=profile["phone"], disabled=True)
                st.text_input("SSN", value=profile["ssn"], disabled=True)
            st.text_input("Role", value=profile["role"], disabled=True)

render_footer()
