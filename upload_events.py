import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from PIL import Image
import io

# Title of the Streamlit app
st.title('Upload Events to Database')
# Date and time input in two columns
col1, col2 = st.columns(2)

with col1:
    event_date = st.date_input("Select the event date", datetime.now().date())

with col2:
    event_time = st.time_input("Select the event time", datetime.now().time())

# Dropdown for selecting event type
event_type = st.selectbox(
    'Select the event you want to upload:',
    ('feeding', 'change beehive box', 'harvest', 'varoa treatment', 'other')
)

# Free text space (optional)
event_description = st.text_area("Event Description (optional)")

# Upload picture using camera (optional)
uploaded_image = st.camera_input("Take a picture (optional)")

# Display the selected event type
st.write(f'You selected: {event_type}')

# Placeholder for future functionality to upload the event to the database
if st.button('Upload Event'):
    st.write(f'Uploading {event_type} event to the database...')
    st.write(f'Event Date: {event_date}')
    st.write(f'Event Time: {event_time}')
    st.write(f'Event Description: {event_description}')
    
    # Combine date and time into a single datetime object
    event_datetime = datetime.combine(event_date, event_time)
    
    # Prepare the data to be inserted
    data = {
        'event_date': event_datetime, 
        'event_type': event_type, 
        'event_description': event_description, 
        'created_on': datetime.now()
    }
    
    if uploaded_image is not None:
        # Convert the image to binary format
        img = Image.open(uploaded_image)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')  # Save image in JPEG format
        img_binary = img_byte_arr.getvalue()   # Convert to binary data

        # Add the binary image data to the event_data
        data['uploaded_image'] = img_binary
        st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)
        st.write("Image uploaded successfully.")
    else:
        data['uploaded_image'] = None
    
    # Add your database upload logic here
    # Read MongoDB URI from secrets.toml
    uri = st.secrets["mongodb"]["uri"]
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Select the database and collection
    db = client["beehive_monitoring"]
    collection = db["bee_events"]
    
    # Insert the data into the collection
    collection.insert_one(data)
    
    st.write("Event uploaded successfully to MongoDB.")

    # Show balloons animation when the event is uploaded
    st.balloons()
