import gspread
from google.oauth2.service_account import Credentials

from extract import get_users_and_bodies
from parse_body import get_user_email_addr_and_fields
from parse_fields import parse_fields

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_client():
    creds = Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES)
    return gspread.authorize(creds)


def append_transaction(sheet_id: str, data: dict, worksheet_name: str = "Transactions"):
    client = get_client()
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)

    row = [
        data["date"],
        data["type"],
        data["category"],
        float(data["amount"]),
        data["currency"],
    ]
    if worksheet.row_count == 0 or not worksheet.get_all_values():
        worksheet.append_row(list(data.keys()))

    row = [
        data["date"],
        data["type"],
        data["category"],
        data["amount"],
        data["currency"],
    ]

    worksheet.append_row(row, value_input_option="USER_ENTERED")


def create_worksheet(spreadsheet: gspread.Spreadsheet, worksheet_name: str = "Transactions") -> gspread.Worksheet:
    '''Creates Transaction worksheet if not there'''
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name, rows=1000, cols=10)

    headers = ["Date", "Type", "Category", "Amount", "Currency"]
    if worksheet.row_values(1) != headers:
        worksheet.update("A1", [headers])
    return worksheet


if __name__ == "__main__":
    users_and_bodies = get_users_and_bodies()
    for user_and_body in users_and_bodies:
        fields = get_user_email_addr_and_fields(user_and_body)
        if fields.get('date') is None:
            continue
        data = parse_fields(fields)

append_transaction("YOUR_SHEET_ID_HERE", data)
