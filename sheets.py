from datetime import datetime
import re
import gspread
from google.oauth2.service_account import Credentials

from store import save_user_sheet


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADERS = ["Date", "Type", "Category", "Amount", "Currency", "Description"]

INSTRUCTIONS_CONTENT = [
    ["Welcome to Ledgerly"],
    [""],
    ["This spreadsheet is automatically updated by Ledgerly whenever you log a transaction."],
    [""],
    ["How it works"],
    ["- Forward a receipt, message, or note describing a transaction to Ledgerly."],
    ["- Ledgerly extracts the date, type, category, amount, and currency."],
    ["- It's added as a new row in the sheet matching that transaction's year (e.g. '2026')."],
    [""],
    ["Columns in each year sheet"],
    ["Date", "When the transaction happened"],
    ["Type", "Income or Expense"],
    ["Category", "e.g. Salary, Food, Transport"],
    ["Amount", "Transaction amount"],
    ["Currency", "Currency code, e.g. SGD"],
    [""],
    ["Tips"],
    ["- A new sheet is created automatically for each year — no setup needed."],
    ["- Don't rename year sheets — Ledgerly looks for them by year (e.g. '2026')."],
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


def add_new_user(user_email: str, sheet_id: str) -> dict:
    """Run once when a user first connects their sheet. Verifies access and seeds it."""
    spreadsheet = get_spreadsheet(sheet_id)
    if spreadsheet is None:
        return {"ok": False, "error": "not_found_or_not_shared"}

    save_user_sheet(user_email, sheet_id)

    seed_spreadsheet(spreadsheet)
    return {"ok": True, "spreadsheet_title": spreadsheet.title}


def get_spreadsheet(sheet_id: str) -> gspread.Spreadsheet:
    client = get_client()
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet


def get_worksheet_for_year(spreadsheet: gspread.Spreadsheet, year: str) -> gspread.Worksheet:
    """Get (or create) the worksheet for a given year, with headers."""
    try:
        worksheet = spreadsheet.worksheet(year)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=year, rows=1000, cols=20, index=1)
        worksheet.update([HEADERS], "A1")
        worksheet.format("A1:F1", {"textFormat": {"bold": True}, "backgroundColor": {
                         "red": 0.26, "green": 0.53, "blue": 0.96}, })

    if worksheet.row_values(1) != HEADERS:
        worksheet.update([HEADERS], "A1")

    return worksheet


def seed_spreadsheet(spreadsheet: gspread.Spreadsheet) -> None:
    """First-time setup: rename the default sheet to Instructions and seed content.
    Year sheets (e.g. '2026') are created lazily as transactions come in.
    Safe to call repeatedly."""
    worksheets = spreadsheet.worksheets()
    existing_titles = {worksheet.title for worksheet in worksheets}

    if "Instructions" in existing_titles:
        return

    default_worksheet = worksheets[0]

    if re.fullmatch(r"\d{4}", default_worksheet.title):
        default_worksheet = spreadsheet.add_worksheet(
            title="Instructions", rows=50, cols=20, index=0)
    else:
        default_worksheet.update_title("Instructions")

    default_worksheet.update(INSTRUCTIONS_CONTENT, "A1")

    format_instructions(default_worksheet)


def format_instructions(default_worksheet: gspread.Worksheet) -> None:
    default_worksheet.format(
        "A1", {"textFormat": {"bold": True, "fontSize": 20}})

    for cell in ["A5", "A10", "A17"]:
        default_worksheet.format(
            cell, {"textFormat": {"bold": True, "fontSize": 14}})
    default_worksheet.format(
        "A19", {"textFormat": {"bold": True, "foregroundColor": {"red": 0.92, "green": 0.26, "blue": 0.21}}})


def parse_entry_date(date_str: str) -> datetime:
    cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", date_str.strip())
    return datetime.strptime(cleaned, "%d/%m/%Y %H:%M:%S")


def maybe_insert_month_divider(worksheet: gspread.Worksheet, entry_dt: datetime) -> None:
    all_values = worksheet.get_all_values()

    if len(all_values) <= 1:
        insert_month_divider(worksheet, entry_dt, row_index=2)
        return

    last_row = all_values[-1]

    if sum(1 for cell in last_row if cell.strip()) <= 1:
        return

    try:
        last_dt = parse_entry_date(last_row[0])
    except (ValueError, IndexError):
        return  # unparseable — prevents a bad divider

    if (last_dt.year, last_dt.month) != (entry_dt.year, entry_dt.month):
        insert_month_divider(worksheet, entry_dt,
                             row_index=len(all_values) + 1)


def insert_month_divider(worksheet: gspread.Worksheet, entry_dt: datetime, row_index: int) -> None:
    label = entry_dt.strftime("%B %Y")
    worksheet.append_row([f"— {label} —"], value_input_option="USER_ENTERED")
    worksheet.merge_cells(f"A{row_index}:F{row_index}")
    worksheet.format(f"A{row_index}:F{row_index}", {
        "textFormat": {"bold": True},
        "horizontalAlignment": "CENTER",
        "backgroundColor": {"red": 0.93, "green": 0.93, "blue": 0.93},
    })


def append_transaction(sheet_id: str, entry: dict):
    spreadsheet = get_spreadsheet(sheet_id)
    entry_dt = parse_entry_date(entry["date"])
    year = str(entry_dt.year)
    worksheet = get_worksheet_for_year(spreadsheet, year)

    maybe_insert_month_divider(worksheet, entry_dt)

    row = [
        entry["date"],
        entry["type"],
        entry["category"],
        entry["amount"],
        entry["currency"],
    ]

    worksheet.append_row(row, value_input_option="USER_ENTERED")

    return
