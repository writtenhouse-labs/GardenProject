import requests
import streamlit as st

from api_client import post
from ui import configure_page, portal_card, render_footer, render_heading, render_nav


configure_page("Careers", "artichoke.png")
render_nav()

with portal_card():
    render_heading("artichoke.png", "Careers", "Join the Garden Project team.")
    st.success("Please log in before submitting your resume.")

    with st.form("career-form"):
        applicant_name = st.text_input("Full Name")
        applicant_position = st.text_input("Position Applying For")
        resume = st.file_uploader("Upload Resume", type=["pdf", "doc", "docx"])
        submitted = st.form_submit_button("Submit Application")

    if submitted:
        payload = {
            "applicant_name": applicant_name,
            "applicant_position": applicant_position,
            "resume_filename": resume.name if resume else "",
        }
        try:
            result = post("/careers/apply", payload)
        except requests.RequestException as exc:
            st.error(f"Could not reach the API: {exc}")
        else:
            st.info(result["message"])

render_footer()
