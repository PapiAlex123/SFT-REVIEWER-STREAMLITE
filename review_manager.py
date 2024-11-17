import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from urllib.parse import urlparse

# Google Sheets URL
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1DWJFUI-Yl7kyy84wU_Gag5SdWkBYNpwOqDWKHONG7k8/edit?gid=1326493068"

# Define specific trainers for Alex Thomas and others with placeholder emails
CUSTOM_TRAINERS = {
    "Alex Thomas": [("Aiyasha P", "email1@"), ("Badar", "email2@"), ("Chukka", "email3@"), ("Deepak Dewan", "email4@"), ("Rushikesh V", "email5@")],
    "Yuvraj Yadav": [("Trainer 1", "email1@"), ("Trainer 2", "email2@"), ("Trainer 3", "email3@"), ("Trainer 4", "email4@"), ("Trainer 5", "email5@")],
    "Dawarr": [("Trainer 1", "email1@"), ("Trainer 2", "email2@"), ("Trainer 3", "email3@"), ("Trainer 4", "email4@"), ("Trainer 5", "email5@")],
    "Disha": [("Trainer 1", "email1@"), ("Trainer 2", "email2@"), ("Trainer 3", "email3@"), ("Trainer 4", "email4@"), ("Trainer 5", "email5@")],
    "Prashanth": [("Trainer 1", "email1@"), ("Trainer 2", "email2@"), ("Trainer 3", "email3@"), ("Trainer 4", "email4@"), ("Trainer 5", "email5@")],
    "Sudama": [("Trainer 1", "email1@"), ("Trainer 2", "email2@"), ("Trainer 3", "email3@"), ("Trainer 4", "email4@"), ("Trainer 5", "email5@")]
}

# Extract Spreadsheet ID from the URL
def extract_spreadsheet_id(sheet_url):
    parsed_url = urlparse(sheet_url)
    path_parts = parsed_url.path.split('/')
    return path_parts[3]  # The spreadsheet ID is the 4th part of the path

# Authenticate with Google Sheets
def connect_to_gsheet(sheet_url, sheet_name):
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('service_account.json', scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# Upload data to Google Sheets
def upload_to_gsheet(sheet_url, sheet_name, data):
    worksheet = connect_to_gsheet(sheet_url, sheet_name)
    worksheet.insert_row(data, index=2)  # Insert data at the second row, below the header

# Streamlit app
st.title("Task Review Manager")

# Step 1: Select Reviewer
reviewer = st.selectbox("Who are you?", options=list(CUSTOM_TRAINERS.keys()))

if reviewer:
    st.success(f"Welcome, {reviewer}!")

    # Get trainers for the selected reviewer
    trainer_options = CUSTOM_TRAINERS[reviewer]  # Fetch predefined trainers with placeholder emails

    # Create a dictionary for quick email lookup
    trainer_emails = {name: email for name, email in trainer_options}

    # State variable to handle success page
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Check if a task has been submitted
    if st.session_state.submitted:
        # Display success message and "Continue Reviewing" button
        st.markdown("<h1 style='text-align: center; color: green;'>Task Review Uploaded Successfully!</h1>", unsafe_allow_html=True)
        if st.button("Continue Reviewing"):
            st.session_state.submitted = False
            st.experimental_rerun()
    else:
        # Step 2: Form to add a new task review
        with st.form("task_review_form"):
            st.header(f"Add a Task Review for {reviewer}")

            # Input fields
            trainer_name = st.selectbox("Trainer Name", options=[name for name, _ in trainer_options])
            batch = st.text_input("Batch")
            task_id = st.text_input("Task ID")
            task_link = st.text_input("Task Link")
            review = st.text_area("Review")
            task_rating = st.number_input(
                "Task Rating",
                min_value=0.0,  # Minimum rating
                max_value=5.0,  # Maximum rating
                value=3.0,  # Default rating
                step=0.1,  # Step size for plus/minus buttons
                format="%.1f"  # Display format
            )
            redo = st.selectbox("Redo/Not Redo", options=["Redo", "Not Redo"])

            # Get the corresponding email
            trainer_email = trainer_emails[trainer_name]

            # Submit button
            submitted = st.form_submit_button("Submit")

        # Handle form submission
        if submitted:
            # Ensure correct column alignment
            row_data = [trainer_name, trainer_email, batch, task_id, task_link, review, task_rating, redo]

            # Save the data to the selected reviewer's Google Sheet tab
            try:
                upload_to_gsheet(GOOGLE_SHEETS_URL, reviewer, row_data)
                st.session_state.submitted = True
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error uploading to Google Sheets: {e}")
