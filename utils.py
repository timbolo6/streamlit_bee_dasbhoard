import streamlit as st
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import plotly.express as px
import requests
import joblib

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
@st.cache_data(ttl=600,show_spinner= "Buzzing in the latest bee data... hold on to your honey!🍯🐝" )
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

@st.cache_data(ttl=600)
def load_events(start_date, end_date, selected_beehive_id):
    """
    Load events from a MongoDB database within the specified date range and for the selected beehive.

    Args:
        start_date (datetime): The start date for filtering events.
        end_date (datetime): The end date for filtering events.
        selected_beehive_id (str): The ID of the selected beehive.

    Returns:
        pd.DataFrame: A DataFrame containing the events data.
    """
    try:
        uri = st.secrets["mongodb"]["uri"]
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client["beehive_monitoring"]
        collection = db["bee_events"]

        # Retrieve the documents with the specified date range from the collection
        cursor = collection.find({
            "event_date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "hive_id": selected_beehive_id
        })

        # Convert cursor to list and create DataFrame
        events_df = pd.DataFrame(list(cursor))

        if events_df.empty:
            st.warning("No events found for the selected date range and beehive.")
        return events_df

    except Exception as e:
        st.error(f"An error occurred while loading events: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error


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

def get_forecast(beehive_id, agg_data, horizon=30):
    """
    Returns the forecasted DataFrame from the start of the filtered input data 
    to 30 days after the last timestamp in the filtered range.
    
    Parameters:
        beehive_id (str): The ID of the beehive
        agg_data (pd.DataFrame): The full dataset with 'timestamp', 'beehive_id', and 'weight'
    
    Returns:
        forecast (pd.DataFrame): Forecasted values from start to end+30d
    """

    # Load the pretrained model
    model = joblib.load(f"./models/prophet_model_{beehive_id}.pkl")

    # Process the data for prediction
    agg_data['timestamp'] = agg_data['timestamp'].dt.tz_localize(None)
    agg_data['weight'] = agg_data['weight'].astype(float)
    agg_data = agg_data[['timestamp', 'weight']].rename(columns={'timestamp': 'ds', 'weight': 'y'}).dropna()

    if agg_data.empty:
        return pd.DataFrame()  # Return empty DataFrame if no data

    start_date = agg_data['ds'].min()
    end_date = agg_data['ds'].max()
    forecast_end_date = end_date + pd.Timedelta(days=horizon)

    # Generate full future frame up to forecast_end_date
    future = model.make_future_dataframe(periods=horizon, freq='D')

    # Predict and filter forecast to desired window
    forecast = model.predict(future)
    forecast_filtered = forecast[(forecast['ds'] >= start_date) & (forecast['ds'] <= forecast_end_date)]

    return forecast_filtered

# Function to calculate and display metrics
def calculate_and_display_metric(data, column_name, column_label,start_date_input,end_date_input, col):
    """
    Calculate and display a metric for the given column and selected month.

    Args:
        column_name (str): The name of the column to calculate the metric for.
        column_label (str): The label to display for the column.
        start_date_input (datetime): The selected start date to calculate the metric for.
        end_date_input (datetime): The selected end date to calculate the metric for.
        col (streamlit.DeltaGenerator): The Streamlit column to display the metric in.

    Returns:
        None
    """
    try:
        start_date_value = data['timestamp'].loc[~data[column_name].isna()].iloc[0]
        end_date_value = data['timestamp'].loc[~data[column_name].isna()].iloc[-1]
        # Calculate the delta between the values from start to end date
        start_value = data[column_name].loc[~data[column_name].isna()].iloc[0]
        end_value = data[column_name].loc[~data[column_name].isna()].iloc[-1]
        delta_value = end_value - start_value
    except IndexError:
        start_date_value = start_date_input
        end_date_value = end_date_input
        start_value = None
        end_value = None
        delta_value = None
    # get unit out of column_label where it is written in brackets
    unit = column_label.split("(")[1].split(")")[0]

    col.metric(
        label=f"Current {column_label}",
        help=f"Range: {start_date_value.strftime('%d.%m.%y')} to {end_date_value.strftime('%d.%m.%y')}",
        value=f"{end_value:.2f}" if end_value is not None else None,
        delta=f"{delta_value:.2f}{unit}" if delta_value is not None else None
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
    

import plotly.graph_objects as go
import streamlit as st

def plot_line_chart(data, sensor, color, line_shape='spline', x='timestamp', forecast_df=None):
    """
    Plots a line chart using Plotly and Streamlit.

    Parameters:
    data (DataFrame): The historical data to plot.
    sensor (str): The column name of the sensor data to plot.
    color (str): The color of the historical line.
    line_shape (str, optional): The shape of the line. Default is 'spline'.
    x (str, optional): The column name for the x-axis. Default is 'timestamp'.
    forecast_df (DataFrame, optional): A Prophet-style forecast DataFrame with 'ds', 'yhat', 'yhat_lower', 'yhat_upper'

    Returns:
    plotly.graph_objs._figure.Figure: The Plotly figure object.
    """
    fig = go.Figure()

    # Plot historical data
    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[sensor],
        mode='lines',
        name='Historical',
        line=dict(color=color, shape=line_shape),
    ))

    # If forecast is provided, overlay forecast + confidence interval
    if forecast_df is not None:
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='gray', dash='dot'),
        ))

        # # Add confidence interval shadow (fill between lower and upper)
        # fig.add_trace(go.Scatter(
        #     x=pd.concat([forecast_df['ds'], forecast_df['ds'][::-1]]),
        #     y=pd.concat([forecast_df['yhat_upper'], forecast_df['yhat_lower'][::-1]]),
        #     fill='toself',
        #     fillcolor='rgba(128, 128, 128, 0.2)',
        #     line=dict(color='rgba(255,255,255,0)'),
        #     hoverinfo="skip",
        #     name='Confidence Interval',
        #     showlegend=False
        # ))

    fig.update_layout(
        height=250,
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False
    )

    return st.plotly_chart(fig, use_container_width=True)
