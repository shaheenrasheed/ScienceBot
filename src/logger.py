import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

class GoogleSheetLogger:
    def __init__(self):
        # 1. Define the scope (permissions)
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        self.creds_path = "data/credentials.json"
        self.client = None
        self.sheet = None
        self.SHEET_NAME = "ScienceBot Logs" # <--- MAKE SURE YOUR SHEET HAS THIS NAME

        # 2. Authenticate
        if os.path.exists(self.creds_path):
            try:
                self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_path, self.scope)
                self.client = gspread.authorize(self.creds)
                
                # Open the Spreadsheet
                # Note: You can open by title OR by URL (safer)
                # self.sheet = self.client.open(self.SHEET_NAME).sheet1
                
                # Let's try opening by name first. 
                # Ensure your Google Sheet file is named EXACTLY "ScienceBot Logs"
                self.sheet = self.client.open(self.SHEET_NAME).sheet1 
                
                print("✅ Connected to Google Sheets")
            except Exception as e:
                print(f"⚠️ Warning: Could not connect to Google Sheets. Error: {e}")
        else:
            print(f"⚠️ Warning: {self.creds_path} not found.")

    def log_interaction(self, question, answer, q_type="General"):
        if not self.sheet:
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare the row
        row = [timestamp, q_type, question, answer]
        
        try:
            # Append the row to the sheet
            self.sheet.append_row(row)
            print("📝 Logged to Sheet")
        except Exception as e:
            print(f"❌ Logging failed: {e}")

# Note: Create a Google Sheet named "ScienceBot Logs" and share it with the client_email inside credentials.json