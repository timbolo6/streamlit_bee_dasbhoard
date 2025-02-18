import streamlit as st
import pandas as pd

def show_honey_harvest_page():
    st.title("🍯 Honey Harvest")

    st.write("""
    Welcome to the **Honey Harvest Log**, where I keep track of all the honey my bees have produced over the years.  
    Every batch is unique, and this table records the details—**taste, texture, and color**—of each harvest.
    """)

    # Create the honey history table
    data = {
        "Year": ["2024", "2024", "2023", "2023"],
        "Type": ["Sommerblüte", "Rapshonig", "Sommerblüte", "Rapshonig"],
        "Amount (kg)": [12, 10, 8, 30],
        "Smoothness": ["Creamy", "Extra Smooth", "Slightly Grainy", "Smooth"],
        "Color": ["Golden", "White", "Amber", "Light Marmor"],
        "Harvest Date": ["August '24", "June '24", "September '23", "Mai '23"],
        "Taste Rating": ["⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐☆", "⭐⭐⭐⭐"],
    }

    df = pd.DataFrame(data)

    st.subheader("📊 Honey Harvest History")
    st.dataframe(df, hide_index=True)

    st.subheader("🐝 What Affects the Honey Each Year?")
    st.write("- 🍃 **Flower sources** – Different nectar = different flavors.")
    st.write("- 🌞 **Weather impact** – More rain? More sunshine? The bees adapt.")
    st.write("- 🐝 **Bee mood** – Just kidding... or am I?")

    st.subheader("💭 Fun Facts From the Hive")
    st.write("🔹 The 2024 Rapshonig was **so smooth**, it could have been butter’s cousin.")
    st.write("🔹 The 2024 Rapshonig was also **so white** like marmor, the rapeseed portion had been very high this year.")
    st.write("🔹 2023’s batch had **a bit of graininess**, but still tasted amazing!")

show_honey_harvest_page()
