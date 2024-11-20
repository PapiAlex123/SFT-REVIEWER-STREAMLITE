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

# Authenticate with Google Sheets using Streamlit Secrets
service_account_info = st.secrets["google_service_account"]
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)

# Connect to Google Sheets
def connect_to_gsheet(sheet_url, sheet_name):
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# Upload data to Google Sheets
def upload_to_gsheet(sheet_url, sheet_name, data):
    worksheet = connect_to_gsheet(sheet_url, sheet_name)
    worksheet.insert_row(data, index=2)  # Insert data at the second row, below the header

# Callback function for form submission
def handle_submission():
    st.session_state.submitted = True

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "trainer_name" not in st.session_state:
    st.session_state.trainer_name = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Streamlit app
st.title("Trainer Task Manager")

# Page: Welcome
if st.session_state.page == "welcome":
    st.markdown("<h2 style='text-align: center;'>Who is this?</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center;'><img src='https://i.giphy.com/media/fnuSiwXMTV3zmYDf6k/giphy.gif' width='300'></div>",
        unsafe_allow_html=True,
    )
    trainer_name = st.selectbox("Select your name to proceed", options=SHEET_NAMES)

    if st.button("Next"):
        if trainer_name:
            st.session_state.trainer_name = trainer_name
            st.session_state.page = "task_submission"
        else:
            st.error("Please select a trainer before proceeding.")

# Page: Task Submission
elif st.session_state.page == "task_submission":
    trainer_name = st.session_state.trainer_name
    st.success(f"Welcome, {trainer_name}! Please proceed to upload your task details.")

    if st.button("Back"):
        st.session_state.page = "welcome"

    if st.session_state.submitted:
        # Success Page
        st.markdown("<h1 style='text-align: center; color: green;'>Well done! Your data has been updated 🎉</h1>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align: center;'><img src='https://i.giphy.com/media/xT77XWum9yH7zNkFW0/giphy.gif' width='300'></div>",
            unsafe_allow_html=True,
        )
        if st.button("Submit Another Task"):
            st.session_state.submitted = False
            st.session_state.page = "task_submission"
    else:
        # Submission Form
        with st.form("sheet_update_form"):
            date = st.date_input("Date", value=datetime.today())
            batch_no = st.text_input("Batch No (Optional)")
            task_id = st.text_input("TASK ID (Optional)")
            task_link = st.text_input("TASK LINK (Required)")
            time_taken = st.text_input("TIME TAKEN")
            total_login_hours = st.text_input("TOTAL LOGIN HOURS (TILL NOW)")
            comments = st.text_area("COMMENTS (Optional)")

            # Use callback for submit button
            st.form_submit_button("Submit", on_click=handle_submission)

        # Handle Form Submission
        if st.session_state.submitted:
            if not task_link.strip():
                st.error("Task Link is required.")
                st.session_state.submitted = False
            else:
                try:
                    row_data = [
                        date.strftime("%Y-%m-%d"),
                        batch_no or "N/A",
                        task_id or "N/A",
                        task_link,
                        time_taken,
                        total_login_hours,
                        comments or "No comments"
                    ]
                    upload_to_gsheet(GOOGLE_SHEETS_URL, trainer_name, row_data)
                    st.session_state.page = "submitted"
                except Exception as e:
                    st.error(f"Error uploading to Google Sheets: {e}")
