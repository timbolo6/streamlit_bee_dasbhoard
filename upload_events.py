import streamlit as st

# Title of the Streamlit app
st.title('Upload Events to Database')

# Dropdown for selecting event type
event_type = st.selectbox(
    'Select the event you want to upload:',
    ('feeding', 'change beehive boxed', 'harvest')
)

# Display the selected event type
st.write(f'You selected: {event_type}')

# Placeholder for future functionality to upload the event to the database
if st.button('Upload Event'):
    st.write(f'Uploading {event_type} event to the database...')
    # Add your database upload logic here