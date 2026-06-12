import streamlit as st

from ui import configure_page, portal_card, render_footer, render_nav


configure_page("Home", "avocado.png")
render_nav()

with portal_card():
    st.title("Welcome to the Garden Project")
    st.markdown(
        "This website analyzes environmental, climatic, and historical agricultural data to predict crop performance and growing conditions. It uses AI-powered similarity analysis to identify patterns and forecast crop yield."
    )
    st.markdown(
        """
        **Sarah Manago**  
        Writtenhouse Labs, LLC  
        sarahwrittenhouse@yahoo.com
        """
    )

render_footer()
