import os
from googleapiclient.discovery import build


def authenticate_sheets(creds):
    return build("sheets", "v4", credentials=creds)


def append_to_sheet(service, row):
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")

    if not spreadsheet_id:
        raise ValueError("GOOGLE_SHEET_ID is missing from .env")

    if not sheet_name:
        raise ValueError("SHEET_NAME is missing from .env")

    # Now using A:K because we have 11 columns
    range_name = f"'{sheet_name}'!A:K"

    body = {
        "values": [row]
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return result