import os
from typing import Optional
import gspread
from sheets import get_spreadsheet

WORKSHEET_NAME = "users"
HEADERS = ["user_email", "sheet_id"]


def get_db_worksheet() -> gspread.Worksheet:
    """Get (or create) the worksheet that holds the user -> sheet_id mapping."""
    spreadsheet = get_spreadsheet(os.environ["USER_SPREADSHEET_ID"])
    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME, rows=1000, cols=len(HEADERS)
        )
        worksheet.append_row(HEADERS)
    return worksheet


def init_db() -> None:
    """Ensure the worksheet and header row exist."""
    worksheet = get_db_worksheet()
    if worksheet.row_values(1) != HEADERS:
        worksheet.update("A1:B1", [HEADERS])


def find_db_row(worksheet: gspread.Worksheet, user_email: str) -> Optional[int]:
    """Return the 1-indexed row number for user_email, or None if not found."""
    try:
        cell = worksheet.find(user_email, in_column=1)
    except gspread.exceptions.CellNotFound:
        return None
    return cell.row if cell else None


def save_user_sheet(user_email: str, sheet_id: str) -> None:
    worksheet = get_db_worksheet()
    row = find_db_row(worksheet, user_email)
    if row is not None:
        worksheet.update(f"B{row}", [[sheet_id]])
    else:
        worksheet.append_row([user_email, sheet_id])


def get_sheet_id_for_user(user_email: str) -> Optional[str]:
    worksheet = get_db_worksheet()
    row = find_db_row(worksheet, user_email)
    if row is None:
        return None
    return worksheet.cell(row, 2).value
