import streamlit as st

home_page = st.Page("app.py", title="Bee Health Monitoring", icon=":material/home:")
upload_events = st.Page("upload_events.py", title="Upload Events", icon=":material/upload:")

pg = st.navigation([home_page, upload_events])
st.set_page_config(page_title="Bee Happy", page_icon=":bee:")
pg.run()
