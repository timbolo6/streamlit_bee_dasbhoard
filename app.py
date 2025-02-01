import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.express as px

from utils import load_raw_data, calculate_and_display_metric, calculate_and_display_rapid_weight_changes, load_events,plot_line_chart,get_external_ip

external_ip = get_external_ip()

# Initialize session state variables if they don't exist
if 'columns_to_plot' not in st.session_state:
    st.session_state.columns_to_plot = ['weight']
if 'start_date_input' not in st.session_state:
    st.session_state.start_date_input = None
if 'end_date_input' not in st.session_state:
    st.session_state.end_date_input = None

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
    """
             "External IP:", external_ip)

#"""Load raw data from MongoDB and CSV file and do some preprocessing"""
data, rapid_weight_data = load_raw_data()
data['timestamp'] = pd.to_datetime(data['timestamp'], format='mixed', yearfirst=True, utc=True)
rapid_weight_data['created_at'] = pd.to_datetime(rapid_weight_data['created_at'])
rapid_weight_data['end_date'] = pd.to_datetime(rapid_weight_data['end_date'])

# Default date range is the last day of data
end_date = data['timestamp'].max()
start_date = end_date - timedelta(days=30)

#"""Sidebar components"""
st.sidebar.title("Settings")
## Sidebar for selecting beehive_id in data
beehive_ids = data['beehive_id'].unique()
selected_beehive_id = st.sidebar.selectbox("Select Beehive ID", beehive_ids)
data = data[data['beehive_id'] == selected_beehive_id]
## Sidebar for column selection
columns_to_plot = st.sidebar.multiselect(
    "Select the columns to plot",
    ['weight', 'temperature', 'humidity'],
    default=st.session_state.columns_to_plot
)
st.session_state.columns_to_plot = columns_to_plot
# Date range filter in sidebar
date_input = st.sidebar.date_input(
    "Select a date range",
    value=(st.session_state.start_date_input or start_date.date(),
           st.session_state.end_date_input or end_date.date()),
    min_value=data['timestamp'].min().date(),
    max_value= pd.to_datetime('today').date(),
    format="DD.MM.YYYY"
)
# Check if both start and end dates are selected
if len(date_input) != 2:
    st.warning("Please select both start and end dates.")
    st.stop()
    
start_date_input, end_date_input = date_input
st.session_state.start_date_input = start_date_input
st.session_state.end_date_input = end_date_input
# Convert the user input to datetime format for filtering, and localize to Europe/Berlin timezone
start_date_input = pd.to_datetime(
    start_date_input).tz_localize('Europe/Berlin')
end_date_input = pd.to_datetime(end_date_input).tz_localize('Europe/Berlin')

#'''FILTERING DATA'''
filtered_data = data[(data['timestamp'] >= start_date_input)
                     & (data['timestamp'] <= end_date_input)]
rapid_weight_data_selected = rapid_weight_data[(rapid_weight_data['end_date'] >= start_date_input) & (
    rapid_weight_data['created_at'] <= end_date_input)]
agg_data = filtered_data.groupby([pd.Grouper(key='timestamp', freq='D'), 'beehive_id']).agg({
    'weight': 'mean',
    'temperature': 'mean',
    'humidity': 'mean'
}).reset_index()


col1, col2, col3 = st.columns(3)

with col1:
    calculate_and_display_metric(agg_data,'weight', 'Weight (kg)',start_date_input,end_date_input, col1)
    plot_line_chart(agg_data,'weight','green')
with col2:
    calculate_and_display_metric(agg_data,'temperature', 'Temp. (°C)',start_date_input,end_date_input, col2)
    plot_line_chart(agg_data,'temperature','red')
with col3:
    calculate_and_display_metric(agg_data,'humidity', 'Humidity (%)',start_date_input,end_date_input, col3)
    plot_line_chart(agg_data,'humidity','blue')

# Plotting Raw Data section
st.write(
    f"#### Raw Data Plotting: {', '.join([col.capitalize() for col in columns_to_plot])} over time")
st.write(f"<span style='color: grey;'>Latest timestamp: {data['timestamp'].max().strftime('%H:%M %d-%m-%Y')}</span>", unsafe_allow_html=True)
fig = px.line(filtered_data.sort_values(by='timestamp'), x='timestamp',
              y=columns_to_plot, line_shape='spline')

# Add intervals from rapid_weight_data_selected
for _, row in rapid_weight_data_selected.iterrows():
    fill_color = "green" if row['weight_diff'] > 0 else "red"
    fig.add_vrect(
        x0=row['created_at'], x1=row['end_date'],
        fillcolor=fill_color, opacity=0.3, line_width=3, line_color=fill_color,
    )
st.plotly_chart(fig)

st.write("### Detection of rapid weight changes events")
# Calculate and display the metric for rapid weight changes
col1, col2, col3 = st.columns(3)
calculate_and_display_rapid_weight_changes(rapid_weight_data,end_date_input, col1)
st.write(rapid_weight_data_selected)
# Adjust start and end date to include the last hour of the day (23:59)
start_date_input = start_date_input.replace(
    hour=0, minute=0, second=0, microsecond=0)
end_date_input = end_date_input.replace(
    hour=23, minute=59, second=59, microsecond=999999)

events_df = load_events(start_date_input, end_date_input)

st.write("### Uploaded Events")
if not events_df.empty:
    st.write(events_df[['event_date', 'event_type',
             'event_description', 'uploaded_image']])
else:
    st.write("No events found in the selected date range.")
