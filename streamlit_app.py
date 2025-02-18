import streamlit as st

home_page = st.Page("app.py", title="Bee Health Monitoring", icon=":material/home:")
upload_events = st.Page("upload_events.py", title="Upload Events", icon=":material/upload:")
honey_harvest = st.Page("honey_harvest.py", title="Honey Harvest", icon=":material/hive:")

pg = st.navigation([home_page, upload_events,honey_harvest])
st.set_page_config(page_title="Bee Happy", page_icon=":bee:")
pg.run()
