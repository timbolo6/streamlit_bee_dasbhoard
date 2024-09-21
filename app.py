# Import necessary libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# Title and description of the app
st.title("Bee Health Monitoring")
st.write("""
This is a simple data app created using Streamlit. You can add different components like text, charts, and data tables.
""")

# Sidebar components (if needed)
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the sidebar to interact")


# Load data
@st.cache_data
def load_data():
    # Load your dataset (update the file path as needed)
    data = pd.read_csv(".streamlit/24-09-21_beehive_cleaned.csv")  
    return data

data = load_data()

# Convert 'created_at' column to datetime if it isn't already
data['created_at'] = pd.to_datetime(data['created_at'])

# Sidebar for column selection
column_to_plot = st.sidebar.selectbox(
    "Select the column to plot",
    ['weight_cleaned', 'temperature', 'humidity']
)

# Default date range is the last day of data
end_date = data['created_at'].max()
start_date = end_date - timedelta(days=1)

# Date range filter in sidebar using st.date_input
start_date_input, end_date_input = st.sidebar.date_input(
    "Select a date range",
    value=(start_date.date(), end_date.date()),
    min_value=data['created_at'].min().date(),
    max_value=data['created_at'].max().date()
)

# Convert the user input to datetime format for filtering, and localize to UTC
start_date_input = pd.to_datetime(start_date_input).tz_localize('UTC')
end_date_input = pd.to_datetime(end_date_input).tz_localize('UTC')
# Filter the dataframe based on the selected date range
filtered_data = data[(data['created_at'] >= start_date_input) & (data['created_at'] <= end_date_input)]

# Plotting section
st.write(f"### Plotting: {column_to_plot.capitalize()} over time")

# Create the line plot
fig, ax = plt.subplots()
ax.plot(filtered_data['created_at'], filtered_data[column_to_plot], label=column_to_plot, color='b')
ax.set_xlabel('Date')
ax.set_ylabel(column_to_plot.capitalize())
ax.set_title(f'{column_to_plot.capitalize()} over Time')
ax.legend()

# Display the plot in Streamlit
st.pyplot(fig)

# Display the data
st.write("### Data Preview")
st.write(filtered_data.head())
