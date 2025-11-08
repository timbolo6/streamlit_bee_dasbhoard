import random
import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.express as px
from app.utils import load_raw_data, calculate_and_display_metric, calculate_and_display_rapid_weight_changes, load_events, plot_line_chart, get_external_ip, get_forecast

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

# """Load raw data from MongoDB and CSV file and do some preprocessing"""
raw_data, rapid_weight_data = load_raw_data()
raw_data.loc[:,'timestamp'] = pd.to_datetime(
    raw_data['timestamp'], format='mixed', yearfirst=True, utc=True)
raw_data.loc[:,'weight'] = pd.to_numeric(raw_data['weight'], errors='coerce')
raw_data.loc[:,'temperature'] = pd.to_numeric(
    raw_data['temperature'], errors='coerce')
raw_data.loc[:,'humidity'] = pd.to_numeric(raw_data['humidity'], errors='coerce')
rapid_weight_data.loc[:,'created_at'] = pd.to_datetime(
    rapid_weight_data['created_at'])
rapid_weight_data.loc[:,'end_date'] = pd.to_datetime(rapid_weight_data['end_date'])

# Default date range is the last day of data
end_date = raw_data['timestamp'].max()
start_date = end_date - timedelta(days=30)

# """Sidebar components"""
st.sidebar.title("Settings")
# Sidebar for selecting beehive_id in data
beehive_ids = sorted(raw_data['beehive_id'].unique().tolist())
st.sidebar.selectbox("Select Beehive ID",
                     options=beehive_ids, key="selected_beehive_id", index=random.randint(0, len(beehive_ids) - 1))

# Sidebar for column selection
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
    min_value=raw_data['timestamp'].min().date(),
    max_value=pd.to_datetime('today').date() + timedelta(days=1),
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
    start_date_input).tz_localize('utc')
end_date_input = pd.to_datetime(end_date_input).tz_localize('Europe/Berlin')

# '''FILTERING DATA'''
raw_data_date_range = raw_data[(raw_data['timestamp'] >= start_date_input)
                               & (raw_data['timestamp'] <= end_date_input + timedelta(days=1))]
rapid_weight_data_selected = rapid_weight_data[(rapid_weight_data['end_date'] >= start_date_input) & (
    rapid_weight_data['created_at'] <= end_date_input)]
agg_data = raw_data_date_range.groupby([pd.Grouper(key='timestamp', freq='D'), 'beehive_id']).agg({
    'weight': 'mean',
    'temperature': 'mean',
    'humidity': 'mean'
}).reset_index()

if st.session_state.selected_beehive_id == "1":
    st.warning(body ="Beehive died due to bee robbery on the 30.07.2025",icon=":material/thumb_down:")
with st.container(border=False):
    col1, col2, col3 = st.columns(3)
    agg_data_selected_beehive = agg_data[agg_data['beehive_id']
                                         == st.session_state.selected_beehive_id]
    raw_data_date_range_selected_beehive = raw_data_date_range[
        raw_data_date_range['beehive_id'] == st.session_state.selected_beehive_id]
    forecast_weight = get_forecast(
        st.session_state.selected_beehive_id, agg_data_selected_beehive, horizon=14)
    
    with col1:
        calculate_and_display_metric(
            raw_data_date_range_selected_beehive, 'weight', 'Weight (kg)', start_date_input, end_date_input, col1)
        plot_line_chart(agg_data_selected_beehive, 'weight', 'green', forecast_df=forecast_weight)
    
    with col2:
        calculate_and_display_metric(raw_data_date_range_selected_beehive, 'temperature',
                                     'Temp. (°C)', start_date_input, end_date_input, col2)
        plot_line_chart(agg_data_selected_beehive, 'temperature', 'red')
    
    with col3:
        calculate_and_display_metric(raw_data_date_range_selected_beehive, 'humidity',
                                     'Humidity (%)', start_date_input, end_date_input, col3)
        plot_line_chart(agg_data_selected_beehive, 'humidity', 'blue')

# Create different tabs
tab1, tab2 = st.tabs(
    ["Raw Data", "Beehive comparison"])
with tab1:
    raw_data_date_range_selected_beehive = raw_data_date_range[
        raw_data_date_range['beehive_id'] == st.session_state.selected_beehive_id]
    st.write(
        f"#### Raw Data: {', '.join([col.capitalize() for col in columns_to_plot])} over the last 7 days")
    st.write(
        f"<span style='color: grey;'>Latest timestamp: {raw_data_date_range_selected_beehive['timestamp'].max().strftime('%H:%M %d-%m-%Y')}</span>", unsafe_allow_html=True)    
    fig = px.line(raw_data_date_range_selected_beehive[(raw_data_date_range_selected_beehive['timestamp'] >= end_date_input - timedelta(days=7))
                                                       & (raw_data_date_range_selected_beehive['timestamp'] <= end_date_input + timedelta(days=7))].sort_values(by='timestamp'), x='timestamp',
                  y=columns_to_plot, line_shape='spline', color_discrete_sequence=['green', 'red', 'blue'])

    # Add intervals from rapid_weight_data_selected
    for _, row in rapid_weight_data_selected.iterrows():
        fill_color = "green" if row['weight_diff'] > 0 else "red"
        fig.add_vrect(
            x0=row['created_at'], x1=row['end_date'],
            fillcolor=fill_color, opacity=0.3, line_width=3, line_color=fill_color,
        )
    st.plotly_chart(fig)
    events_df = load_events(start_date_input, end_date_input, selected_beehive_id=st.session_state.selected_beehive_id)
    if events_df.empty:
      pass
    else:
        st.write("### Events")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Uploaded Events", len(events_df), delta_color="normal")
        with col2:
            calculate_and_display_rapid_weight_changes(
            rapid_weight_data, end_date_input, col2)
        
        aframe(events_df[['event_date', 'event_type',
                                'event_description', 'uploaded_image']].sort_values(by='event_date', ascending=False))
        st.dataframe(rapid_weight_data_selected)
        # Adjust start and end date to include the last hour of the day (23:59)
        start_date_input = start_date_input.replace(
            hour=0, minute=0, second=0, microsecond=0)
        end_date_input = end_date_input.replace(
            hour=23, minute=59, second=59, microsecond=999999)

with tab2:
    st.write(
        f"#### {', '.join([col.capitalize() for col in columns_to_plot])} Comparison")
    random_beehive_id = random.choice(
        [beehive_id for beehive_id in beehive_ids if beehive_id != st.session_state.selected_beehive_id])
    # Create a multi-select box for beehive IDs
    selected_beehives = st.multiselect(
        "Select Beehive IDs to compare",
        options=beehive_ids,
        default=[st.session_state.selected_beehive_id, random_beehive_id]
    )
    normalize_data = st.checkbox("Normalize data to get relative change", value=True, help="Normalize each selected column per beehive, starting at 100%. For example: Sensor A starts at 50g, Sensor B at 100g — but both grow 20%. This will show both going from 100 to 120 (as %), highlighting relative change independent of initial value.")

    if selected_beehives: 
        filtered_data_comparison = agg_data[agg_data['beehive_id'].isin(selected_beehives)]

    if normalize_data:
        # Normalize each selected column per beehive, starting at 100%
        for col in columns_to_plot:
            filtered_data_comparison[col] = filtered_data_comparison.groupby('beehive_id')[col].transform(
                lambda x: (x / x.iloc[0]) * 100
            )
        y_axis_title = "Relative Change (%)<br><span style='font-size: smaller;'>Initial = 100%</span>"
    else:
        y_axis_title = "Value"

    fig = px.line(
        filtered_data_comparison,
        x='timestamp',
        y=columns_to_plot,
        color='beehive_id',
        line_shape='spline',
        color_discrete_sequence=['orange', 'purple', 'grey']
    )
    fig.update_yaxes(title_text=y_axis_title)
    st.plotly_chart(fig)



    

