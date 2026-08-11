import gspread
from google.oauth2.service_account import Credentials

from extract import get_users_and_bodies
from parse_body import get_user_email_addr_and_fields
from parse_fields import parse_fields, parse_data

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ["Date", "Type", "Category", "Amount", "Currency"]

INSTRUCTIONS_CONTENT = [
    ["Welcome to Ledgerly 📒"],
    [""],
    ["This spreadsheet is automatically updated by Ledgerly whenever you log a transaction."],
    [""],
    ["How it works"],
    ["- Forward a receipt, message, or note describing a transaction to Ledgerly."],
    ["- Ledgerly extracts the date, type, category, amount, and currency."],
    ["- It's added as a new row in the 'Transactions' tab."],
    [""],
    ["Columns in Transactions"],
    ["Date", "When the transaction happened"],
    ["Type", "Income or Expense"],
    ["Category", "e.g. Salary, Food, Transport"],
    ["Amount", "Transaction amount"],
    ["Currency", "Currency code, e.g. SGD"],
    [""],
    ["Tips"],
    ["- Don't rename the 'Transactions' tab — Ledgerly looks for it by name."],
    ["- Feel free to add your own charts, pivot tables, or extra tabs elsewhere in this sheet."],
]

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


def seed_spreadsheet(spreadsheet: gspread.Spreadsheet) -> None:
    """First-time setup: rename the default sheet to Instructions and seed content,
    then ensure a Transactions worksheet exists. Safe to call repeatedly."""
    worksheets = spreadsheet.worksheets()
    existing_titles = {worksheet.title for worksheet in worksheets}

    if "Instructions" not in existing_titles:
        default_worksheet = worksheets[0]
        if default_worksheet.title == "Transactions":
            default_worksheet = spreadsheet.add_worksheet(
                title="Instructions", rows=50, cols=5, index=0)
        else:
            default_worksheet.update_title("Instructions")

        default_worksheet.update(INSTRUCTIONS_CONTENT, "A1")
        default_worksheet.format(
            # Makes the instructions page nice
            # TODO: Make the instructions page also transaction page
            "A1", {"textFormat": {"bold": True, "fontSize": 14}})

    get_worksheet(spreadsheet, "Transactions")
    return


def append_transaction(sheet_id: str, entry: dict, worksheet_name: str = "Transactions"):
    spreadsheet = get_spreadsheet(sheet_id)
    seed_spreadsheet(spreadsheet)
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
        # TODO: Allow for multiple users, (store the id email pair somewhere)
        append_transaction(
            "1E7G5aDH6Spx4wKx3oIXk2kxNbjHRigw1Y0zAWH7eT4A", entry)
