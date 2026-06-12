from ui import configure_page, portal_card, render_footer, render_heading, render_nav


configure_page("Contact Us", "onion.png")
render_nav()

with portal_card():
    render_heading("onion.png", "Contact Us", "Placeholder for the Garden Project Employee Portal.")

render_footer()
