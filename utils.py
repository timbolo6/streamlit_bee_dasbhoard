import streamlit as st
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import plotly.express as px
import requests

def get_external_ip():
    """
    Fetches the external IP address of the machine using the ipify API.

    Returns:
        str: The external IP address if the request is successful, otherwise "Unknown".
    """
    response = requests.get("https://api64.ipify.org?format=json")
    if response.status_code == 200:
        data = response.json()
        return data.get("ip")
    else:
        return "Unknown"

# Load data
@st.cache_data(ttl=3600)
def load_raw_data():
    uri = st.secrets["mongodb"]["uri"]
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["beehive_monitoring"]
    collection = db["bee_sensor_telemetry"]
    # Retrieve all documents from the collection
    cursor = collection.find({})
    # Convert cursor to list and create DataFrame
    sensor_data = pd.DataFrame(list(cursor))
    rapid_weight_data = pd.read_csv(
        ".streamlit/rapid_weight_changes_events.csv")
    return sensor_data, rapid_weight_data

@st.cache_data(ttl=3600)
def load_events(start_date, end_date):
    # Display events from a MongoDB database in the selected date range
    uri = st.secrets["mongodb"]["uri"]
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["beehive_monitoring"]
    collection = db["bee_events"]

    # Retrieve the documents with the specified date range from the collection
    cursor = collection.find({
        "event_date": {
            "$gte": start_date,
            "$lte": end_date
        }
    })
    # Convert cursor to list and create DataFrame
    events_df = pd.DataFrame(list(cursor))
    return events_df


@st.cache_data
def load_agg_data(selected_beehive_id, start_date_input, end_date_input):
    uri = st.secrets["mongodb"]["uri"]
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["beehive_monitoring"]
    collection = db["bee_sensor_telemetry_agg"]
    cursor = collection.find({
        "beehive_id": selected_beehive_id,
        "timestamp": {
            "$gte": start_date_input,
            "$lte": end_date_input
        }
    })
    agg_data = pd.DataFrame(list(cursor))
    return agg_data


# Function to calculate and display metrics
def calculate_and_display_metric(data, column_name, column_label, selected_month, col):
    """
    Calculate and display a metric for the given column and selected month.

    Args:
        column_name (str): The name of the column to calculate the metric for.
        column_label (str): The label to display for the column.
        selected_month (datetime): The selected month to calculate the metric for.
        col (streamlit.DeltaGenerator): The Streamlit column to display the metric in.

    Returns:
        None
    """
    current_month = selected_month.month
    current_year = selected_month.year
    current_month_data = data[(data['timestamp'].dt.month == current_month) & (
        data['timestamp'].dt.year == current_year)]
    current_month_avg = current_month_data[column_name].mean()
    previous_years_data = data[(data['timestamp'].dt.month == current_month) & (
        data['timestamp'].dt.year < current_year)]
    previous_years_avg = previous_years_data[column_name].mean()
    col.metric(
        label=f"Avg. {column_label} {selected_month.strftime('%B %Y')}",
        value=f"{current_month_avg:.2f}",
        delta=f"{current_month_avg - previous_years_avg:.2f} vs previous years"
    )



def calculate_and_display_rapid_weight_changes(rapid_weight_data,selected_month, col):
    """
    Calculate and display the number of rapid weight changes for the selected month 
    and compare it with the average number of rapid weight changes in the same month 
    from previous years.

    Args:
        selected_month (datetime): The month and year for which to calculate rapid weight changes.
        col (streamlit.DeltaGenerator): The Streamlit column object where the metric will be displayed.

    Returns:
        None
    """
    current_month = selected_month.month
    current_year = selected_month.year
    current_month_data = rapid_weight_data[(rapid_weight_data['created_at'].dt.month == current_month) & (
        rapid_weight_data['created_at'].dt.year == current_year)]
    rapid_weight_event_current_month = current_month_data.shape[0]
    previous_years_data = rapid_weight_data[(rapid_weight_data['created_at'].dt.month == current_month) & (
        rapid_weight_data['created_at'].dt.year < current_year)]
    previous_years_avg = previous_years_data.shape[0] / \
        previous_years_data['created_at'].dt.year.nunique()
    col.metric(
        label=f"N° rapid weight changes {selected_month.strftime('%B %Y')}",
        value=f"{rapid_weight_event_current_month}",
        delta=f"{rapid_weight_event_current_month - previous_years_avg:.2f} vs previous years"
    )
    

def plot_line_chart(data, sensor, color, line_shape='spline', x='timestamp'):
    """
    Plots a line chart using Plotly and Streamlit.

    Parameters:
    data (DataFrame): The data to plot.
    sensor (str): The column name of the sensor data to plot.
    color (str): The color of the line.
    line_shape (str, optional): The shape of the line. Default is 'spline'.
    x (str, optional): The column name for the x-axis. Default is 'timestamp'.

    Returns:
    plotly.graph_objs._figure.Figure: The Plotly figure object.
    """
    fig = px.line(data, x=x, y=sensor, line_shape=line_shape)
    fig.update_traces(line=dict(color=color))
    fig.update_layout(height=300, xaxis_title=None, yaxis_title=None)
    return st.plotly_chart(fig, use_container_width=True)