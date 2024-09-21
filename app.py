# Import necessary libraries
import streamlit as st
import pandas as pd


# Title and description of the app
st.title("Your Streamlit Data App")
st.write("""
This is a simple data app created using Streamlit. You can add different components like text, charts, and data tables.
""")

# Sidebar components (if needed)
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the sidebar to interact")


# Load data
@st.cache
def load_data():
    data = pd.read_csv(".streamlit/24-09-21_beehive_cleaned.csv")  # Load your dataset
    return data

data = load_data()

# Display the data
st.write("### Data Preview")
st.write(data.head())