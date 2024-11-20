import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from urllib.parse import urlparse
from datetime import datetime

# Google Sheets URL
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/10uXSI6X9ZJ9spQWadRhStUmZ-PBhQuCQOtlKc4AsjWc/edit?gid=0"

# Define the sheet names (trainers)
SHEET_NAMES = ["Deepak Dewan", "Chukka Hemalatha", "Badar Unnisa", "Rushikesh Vishwasrao", "Aiyasha Parveen Hilali"]

# Extract Spreadsheet ID from the URL
def extract_spreadsheet_id(sheet_url):
    parsed_url = urlparse(sheet_url)
    path_parts = parsed_url.path.split('/')
    return path_parts[3]  # The spreadsheet ID is the 4th part of the path

# Authenticate with Google Sheets
def connect_to_gsheet(sheet_url, sheet_name):
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('service_account.json', scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# Upload data to Google Sheets
def upload_to_gsheet(sheet_url, sheet_name, data):
    worksheet = connect_to_gsheet(sheet_url, sheet_name)
    worksheet.insert_row(data, index=2)  # Insert data at the second row, below the header

# Streamlit app
st.title("Trainer Task Manager")

# Manage page navigation using session state
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# Page: Welcome
if st.session_state.page == "welcome":
    st.markdown("<h2 style='text-align: center;'>Who is this?</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center;'><img src='https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExdW1rYmpkNGJ2d2x0YWdsNWExZXNlYmh2d2s1dm5wNms3cTRobHNmMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fnuSiwXMTV3zmYDf6k/giphy.gif' width='300'></div>",
        unsafe_allow_html=True,
    )
    trainer_name = st.selectbox("Select your name to proceed", options=SHEET_NAMES)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Next"):
            st.session_state.trainer_name = trainer_name
            st.session_state.page = "task_submission"
            st.experimental_rerun()

# Page: Task Submission
elif st.session_state.page == "task_submission":
    trainer_name = st.session_state.trainer_name
    st.success(f"Welcome, {trainer_name}! Please proceed to upload your task details.")

    # Back button in case the wrong name was selected
    if st.button("Back"):
        st.session_state.page = "welcome"
        st.experimental_rerun()

    # State variable to handle success page
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Check if data has been submitted
    if st.session_state.submitted:
        # Success message and GIF
        st.markdown("<h1 style='text-align: center; color: green;'>Well done! Your data has been updated 🎉</h1>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align: center;'><img src='https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcXptM2c2YzJxcWY3bGhic2xmOHVkODF3Yzh6dXB2MXN1cWUzNXh4aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT77XWum9yH7zNkFW0/giphy.gif' width='300'></div>",
            unsafe_allow_html=True,
        )
        if st.button("Submit Another Task"):
            st.session_state.submitted = False
            st.experimental_rerun()
    else:
        # Input fields for the task
        with st.form("sheet_update_form"):
            date = st.date_input("Date", value=datetime.today())  # Default to today's date
            batch_no = st.text_input("Batch No (Optional)")
            task_id = st.text_input("TASK ID (Optional)")
            task_link = st.text_input("TASK LINK (Required)")
            time_taken = st.text_input("TIME TAKEN")
            total_login_hours = st.text_input("TOTAL LOGIN HOURS (TILL NOW)")
            comments = st.text_area("COMMENTS (Optional)")  # Optional comments

            # Submit button
            submitted = st.form_submit_button("Submit")

        # Handle form submission
        if submitted:
            if not task_link.strip():
                st.error("Task Link is required. Please provide a valid link.")
            else:
                # Prepare the row data
                row_data = [
                    date.strftime("%Y-%m-%d"),  # Format the date
                    batch_no or "N/A",  # Default to "N/A" if blank
                    task_id or "N/A",  # Default to "N/A" if blank
                    task_link,
                    time_taken,
                    total_login_hours,
                    comments or "No comments"  # Default to "No comments" if blank
                ]

                # Upload the data to the selected sheet
                try:
                    upload_to_gsheet(GOOGLE_SHEETS_URL, trainer_name, row_data)
                    st.session_state.submitted = True
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error uploading to Google Sheets: {e}")
