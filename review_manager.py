import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from urllib.parse import urlparse
from datetime import datetime

# Google Sheets URL
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/10uXSI6X9ZJ9spQWadRhStUmZ-PBhQuCQOtlKc4AsjWc/edit?gid=0"

# Define the sheet names (trainers)
SHEET_NAMES = ["Deepak Dewan", "Chukka Hemalatha", "Badar Unnisa", "Rushikesh Vishwasrao", "MD SHARIA", "Raushan Raj"]

# Extract Spreadsheet ID from the URL
def extract_spreadsheet_id(sheet_url):
    parsed_url = urlparse(sheet_url)
    path_parts = parsed_url.path.split('/')
    return path_parts[3]  # The spreadsheet ID is the 4th part of the path

# Authenticate with Google Sheets using Streamlit secrets
def connect_to_gsheet(sheet_url, sheet_name):
    service_account_info = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# Upload data to Google Sheets
def upload_to_gsheet(sheet_url, sheet_name, data):
    worksheet = connect_to_gsheet(sheet_url, sheet_name)
    worksheet.insert_row(data, index=2)  # Insert data at the second row, below the header

# Navigation helpers
def set_page(page_name):
    """Set the current page."""
    st.session_state.page = page_name

def reset_submission():
    """Reset the submission state."""
    st.session_state.submitted = False

# Ensure session state variables are initialized
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
    trainer_name = st.selectbox("Select your name to proceed", options=SHEET_NAMES, key="trainer_select")
    if st.button("Next"):
        st.session_state.trainer_name = trainer_name
        set_page("task_submission")

# Page: Task Submission
elif st.session_state.page == "task_submission":
    trainer_name = st.session_state.trainer_name
    st.success(f"Welcome, {trainer_name}! Please proceed to upload your task details.")
    if st.button("Back to Welcome"):
        set_page("welcome")

    # Submission Form
    with st.form("sheet_update_form"):
        date = st.date_input("Date", value=datetime.today())
        task_link = st.text_input("Task Link (Required)")
        is_rework = st.radio("Is this task a rework?", options=["No", "Yes"], index=0)
        submitted = st.form_submit_button("Submit")

    # Handle form submission
    if submitted:
        if not task_link.strip():
            st.error("Task Link is required. Please provide a valid link.")
        else:
            row_data = [
                date.strftime("%Y-%m-%d"),  # Format the date
                task_link,
                is_rework  # Yes or No for Rework
            ]
            try:
                upload_to_gsheet(GOOGLE_SHEETS_URL, trainer_name, row_data)
                st.session_state.submitted = True
                set_page("submission_success")
            except Exception as e:
                st.error(f"Error uploading to Google Sheets: {e}")

# Page: Submission Success
elif st.session_state.page == "submission_success":
    st.markdown("<h1 style='text-align: center; color: green;'>Well done! Your data has been updated 🎉</h1>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center;'><img src='https://i.giphy.com/media/xT77XWum9yH7zNkFW0/giphy.gif' width='300'></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="text-align: center; font-size: 16px;">Your data has been successfully submitted. If you need to make changes, click below:</p>'
        f'<p style="text-align: center;"><a href="{GOOGLE_SHEETS_URL}" target="_blank">Edit manually in Google Sheets</a></p>',
        unsafe_allow_html=True,
    )

    if st.button("Submit Another Task"):
        reset_submission()
        set_page("task_submission")

    if st.button("Back to Welcome"):
        reset_submission()
        set_page("welcome")
