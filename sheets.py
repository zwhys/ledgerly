import gspread
from google.oauth2.service_account import Credentials

from extract import get_users_and_bodies
from parse_body import get_user_email_addr_and_fields
from parse_fields import parse_fields, parse_data

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ["Date", "Type", "Category", "Amount", "Currency"]

_client = None


def get_client() -> gspread.Client:
    global _client
    if _client is None:
        creds = Credentials.from_service_account_file(
            "service_account.json", scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def get_spreadsheet(sheet_id: str) -> gspread.Spreadsheet:
    client = get_client()
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet


def get_worksheet(spreadsheet: gspread.Spreadsheet, worksheet_name: str = "Transactions") -> gspread.Worksheet:
    '''Gets worksheet (Creates  worksheet if nonexistent)'''
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name, rows=1000, cols=10)

    if worksheet.row_values(1) != HEADERS:
        worksheet.update([HEADERS], "A1")

    return worksheet


def append_transaction(sheet_id: str, entry: dict, worksheet_name: str = "Transactions"):
    spreadsheet = get_spreadsheet(sheet_id)
    worksheet = get_worksheet(spreadsheet, worksheet_name)

    if worksheet.row_count == 0 or not worksheet.get_all_values():
        worksheet.append_row(HEADERS)

    row = [
        entry["date"],
        entry["type"],
        entry["category"],
        entry["amount"],
        entry["currency"],
    ]

    worksheet.append_row(row, value_input_option="USER_ENTERED")
    return


if __name__ == "__main__":
    users_and_bodies = get_users_and_bodies()
    for user_and_body in users_and_bodies:
        fields = get_user_email_addr_and_fields(user_and_body)
        if fields.get('date') is None:
            continue
        entry = parse_data(fields)
        append_transaction("1E7G5aDH6Spx4wKx3oIXk2kxNbjHRigw1Y0zAWH7eT4A", entry) #TODO: Allow for multiple users, (store the id email pair somewhere)
