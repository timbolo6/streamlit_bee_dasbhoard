# Import necessary libraries
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Title and description of the app
st.title("Bee Health Monitoring")
with st.expander("About this app"):
    st.write("""
    Welcome to the Bee Health Monitoring Dashboard. This application is designed to help beekeepers and researchers monitor the health of bee colonies by visualizing key metrics such as weight, temperature, and humidity. 

    ### Features:
    - **Interactive Plots**: Select different metrics to visualize over time.
    - **Date Range Filter**: Easily filter data by selecting a date range.
    - **Data Preview**: View a snapshot of the filtered data.

    Use the sidebar to navigate through the options and customize your view. This tool aims to provide insights into the environmental conditions affecting bee health and help in making informed decisions.
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


# Sidebar for column selection (allow multiple selections)
columns_to_plot = st.sidebar.multiselect(
    "Select the columns to plot",
    ['weight_cleaned', 'temperature', 'humidity'],
    default=['weight_cleaned','temperature'] 
)

# Default date range is the last day of data
end_date = data['created_at'].max()
start_date = end_date - timedelta(days=7)  # Default date range is 7 days

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


# Function to calculate and display metrics
def calculate_and_display_metric(column_name, column_label, selected_month, col):
    """
    Calculate and display a metric comparing the average value of a specified column for the current month 
    with the average value for the same month in previous years.
    Args:
        column_name (str): The name of the column to calculate the average for.
        column_label (str): The label to display for the column in the metric.
        selected_month (datetime): The month and year to calculate the metric for.
        col (streamlit.DeltaGenerator): The Streamlit column to display the metric in.
    Returns:
        None
    """
    current_month = selected_month.month
    current_year = selected_month.year
    # Calculate the average for the current month
    current_month_data = data[(data['created_at'].dt.month == current_month) & (data['created_at'].dt.year == current_year)]
    current_month_avg = current_month_data[column_name].mean()
    
    # Calculate the average for the same month in all previous years
    previous_years_data = data[(data['created_at'].dt.month == current_month) & (data['created_at'].dt.year < current_year)]
    previous_years_avg = previous_years_data[column_name].mean()
    
    # Display the metric
    col.metric(
        label=f"Avg. {column_label} {end_date_input.strftime('%B %Y')}",
        value=f"{current_month_avg:.2f}",
        delta=f"{current_month_avg - previous_years_avg:.2f} vs previous years"
    )

# Create three columns
col1, col2, col3 = st.columns(3)

# Calculate and display metrics for weight, temperature, and humidity
calculate_and_display_metric('weight_cleaned', 'Weight (kg)', end_date_input, col1)
calculate_and_display_metric('temperature', 'Temp. (°C)', end_date_input, col2)
calculate_and_display_metric('humidity', 'Humidity (%)', end_date_input, col3)



# Plotting section
st.write(f"### Plotting: {', '.join([col.capitalize() for col in columns_to_plot])} over time")

# Create a line chart for the selected columns
st.line_chart(filtered_data.set_index('created_at')[columns_to_plot])

# Display the data
st.write("### Data Preview")
st.write(filtered_data.head())
