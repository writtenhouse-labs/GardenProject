import streamlit as st

from ui import configure_page, initialize_session, portal_card, render_footer, render_heading, render_nav


configure_page("Logout", "corn.png")
initialize_session()

st.session_state["logged_in"] = False
st.session_state["user_email"] = ""
st.session_state["user_role"] = ""

render_nav()

with portal_card():
    render_heading("corn.png", "Logged Out", "You are now logged out. Please log in again.")
    st.markdown("[Go to Login](/Login)")

render_footer()
