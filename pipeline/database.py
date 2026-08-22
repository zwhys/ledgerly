import os
from typing import Optional
import gspread
from pipeline.sheets import get_spreadsheet, seed_spreadsheet

WORKSHEET_NAME = "users"
HEADERS = ["chat_id", "email", "sheet_id"]

COL_CHAT_ID = 1
COL_EMAIL = 2
COL_SHEET_ID = 3


_db_worksheet: gspread.Worksheet | None = None
_user_sheet_ids: dict[str, str] = {}


def get_db_worksheet() -> gspread.Worksheet:
    """Get (or create) the worksheet that holds the user -> sheet_id -> chat_id mapping."""

    global _db_worksheet

    if _db_worksheet is not None:
        return _db_worksheet

    spreadsheet = get_spreadsheet(os.environ["USER_SPREADSHEET_ID"])

    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(HEADERS),
        )
        worksheet.append_row(HEADERS)

    _db_worksheet = worksheet
    return worksheet


def find_db_row(worksheet: gspread.Worksheet, chat_id) -> Optional[int]:
    """Return the 1-indexed row number for chat_id, or None if not found."""
    try:
        cell = worksheet.find(chat_id, in_column=COL_CHAT_ID)
    except ValueError:
        return None
    return cell.row if cell else None


def save_email(chat_id: str, email: str) -> None:
    """Create or update a row for this user, recording their email."""
    worksheet = get_db_worksheet()
    row = find_db_row(worksheet, chat_id)

    if row is not None:
        worksheet.update(f"B{row}", [[email]])
    else:
        worksheet.append_row([chat_id, email, ""])


def save_user_sheet(chat_id: str, sheet_id: str) -> None:
    worksheet = get_db_worksheet()

    row = find_db_row(worksheet, chat_id)

    if row is not None:
        worksheet.update(f"C{row}", [[sheet_id]])
    else:
        worksheet.append_row([chat_id, "", sheet_id])

    _user_sheet_ids[chat_id] = sheet_id


def connect_user_sheet(chat_id: str, sheet_id: str) -> dict:
    """Run once when a user first connects their sheet. Verifies access and seeds it."""
    spreadsheet = get_spreadsheet(sheet_id)
    if spreadsheet is None:
        return {"ok": False, "error": "not_found_or_not_shared"}

    save_user_sheet(chat_id, sheet_id)

    seed_spreadsheet(spreadsheet)
    return {"ok": True, "spreadsheet_title": spreadsheet.title}


def get_sheet_id_for_user(chat_id: str) -> Optional[str]:
    if chat_id in _user_sheet_ids:
        return _user_sheet_ids[chat_id]

    worksheet = get_db_worksheet()
    row = find_db_row(worksheet, chat_id)

    if row is None:
        return None

    sheet_id = worksheet.cell(row, COL_SHEET_ID).value

    if sheet_id:
        _user_sheet_ids[chat_id] = sheet_id

    return sheet_id


def get_email_for_chat(chat_id: str) -> Optional[str]:
    worksheet = get_db_worksheet()
    row = find_db_row(worksheet, chat_id)

    if row is None:
        return None

    return worksheet.cell(row, COL_EMAIL).value
