import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
from urllib.parse import urlparse

# Google Sheets URL (replace with your sheet URL)
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/10uXSI6X9ZJ9spQWadRhStUmZ-PBhQuCQOtlKc4AsjWc/edit?gid=0"
SHEET_NAME = "Sheet8"  # Update if needed

# --- Helper Functions ---

# Extract Spreadsheet ID from the URL
def extract_spreadsheet_id(sheet_url):
    parsed_url = urlparse(sheet_url)
    path_parts = parsed_url.path.split('/')
    return path_parts[3]  # The spreadsheet ID is the 4th part of the path

# Connect to Google Sheet
def connect_to_gsheet(sheet_url, sheet_name):
    service_account_info = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# Initialize sheet with headers if empty
def initialize_sheet(worksheet):
    existing_headers = worksheet.row_values(1)
    required_headers = ["username", "timestamp"]
    if existing_headers != required_headers:
        worksheet.clear()
        worksheet.append_row(required_headers)

# Upload username if not duplicate
def upload_username(username, worksheet):
    usernames = [row[0] for row in worksheet.get_all_values()[1:]]  # Skip header
    if username in usernames:
        return False
    timestamp = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    worksheet.insert_row([username, timestamp], index=2)
    return True

# --- Streamlit UI ---

st.title("📋 TikTok Username Submission")

username_input = st.text_input("Enter TikTok username:")

if st.button("Submit Username"):
    if not username_input.strip():
        st.warning("⚠️ Please enter a valid username.")
    else:
        worksheet = connect_to_gsheet(GOOGLE_SHEETS_URL, SHEET_NAME)
        initialize_sheet(worksheet)
        success = upload_username(username_input.strip(), worksheet)
        if success:
            st.success(f"✅ Username `{username_input}` added successfully.")
        else:
            st.error("❌ Username already exists in the sheet.")

# Optional: View all usernames
if st.checkbox("📄 Show saved usernames"):
    worksheet = connect_to_gsheet(GOOGLE_SHEETS_URL, SHEET_NAME)
    data = worksheet.get_all_records()
    st.dataframe(data)
