from __future__ import annotations
import datetime as dt
from typing import Any, Optional
import gspread
from google.oauth2.service_account import Credentials


class SheetsClient:
    def __init__(self, service_account_file: str, spreadsheet_id: str, worksheet_title: Optional[str] = None):
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id
        self.worksheet_title = worksheet_title
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        self.creds = Credentials.from_service_account_file(service_account_file, scopes=scopes)
        self.gc = gspread.authorize(self.creds)
        sh = self.gc.open_by_key(spreadsheet_id)
        if worksheet_title:
            try:
                self.sheet = sh.worksheet(worksheet_title)
            except gspread.WorksheetNotFound:
                # fallback: create the sheet
                self.sheet = sh.add_worksheet(title=worksheet_title, rows=1000, cols=20)
        else:
            self.sheet = sh.sheet1

    def save_booking_data(
        self,
        name: str,
        phone: str,
        service: str,
        datetime: str,
        master_category: str,
        comments: str | None = None,
    ) -> dict[str, Any]:
        """Append a row with the booking data. Returns a small result dict."""
        timestamp = dt.datetime.utcnow().isoformat()
        row = [
            timestamp,
            name,
            phone,
            service,
            datetime,
            master_category,
            comments or "",
        ]
        try:
            self.sheet.append_row(row, value_input_option="USER_ENTERED")
            return {"status": "ok", "appended": row}
        except Exception as e:
            return {"status": "error", "message": str(e), "row": row}
