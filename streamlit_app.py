import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))
st.set_page_config(page_title="Bee Happy", page_icon=":bee")

pages = [
    st.Page("src/app/honey_order.py", title="Order Honey", icon=":material/shopping_cart:"),
    st.Page("src/app/bee_monitoring.py", title="Bee Health", icon=":material/analytics:"),
    st.Page("src/app/upload_events.py", title="Upload Events", icon=":material/upload:"),
    st.Page("src/app/honey_harvest.py", title="Honey Harvest", icon=":material/hive:"),
    
]

pg = st.navigation(pages, position="top")
pg.run()
