import os
from typing import Optional
import gspread
from pipeline.sheets import get_spreadsheet, seed_spreadsheet

WORKSHEETS = {
    "users": ["chat_id", "email", "sheet_id"],
    "pending": ["transaction_id", "sheet_id", "entry"],
}


COL_CHAT_ID = 1
COL_EMAIL = 2
COL_SHEET_ID = 3


_db_worksheets: dict[str, gspread.Worksheet] = {}
_user_sheet_ids: dict[str, str] = {}
_telegram_chat_ids: dict[str, str] = {}


def get_db_worksheet(name: str) -> gspread.Worksheet:
    if name in _db_worksheets:
        return _db_worksheets[name]

    headers = WORKSHEETS[name]
    spreadsheet = get_spreadsheet(os.environ["USER_SPREADSHEET_ID"])

    try:
        worksheet = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=name,
            rows=1000,
            cols=len(headers),
        )
        worksheet.append_row(headers)

    _db_worksheets[name] = worksheet
    return worksheet


def find_db_row(
    worksheet: gspread.Worksheet,
    chat_id: str | None = None,
    email: str | None = None,
    sheet_id: str | None = None
) -> Optional[int]:
    """Return the 1-indexed row number for chat_id or email, or None if not found."""

    if chat_id:
        try:
            cell = worksheet.find(chat_id, in_column=COL_CHAT_ID)
            return cell.row if cell else None
        except ValueError:
            pass

    if email:
        try:
            cell = worksheet.find(email, in_column=COL_EMAIL)
            return cell.row if cell else None
        except ValueError:
            pass

    if sheet_id:
        try:
            cell = worksheet.find(sheet_id, in_column=COL_SHEET_ID)
            return cell.row if cell else None
        except ValueError:
            pass

    return None


def save_email(chat_id: str, email: str) -> None:
    """Create or update a row for this user, recording their email."""
    worksheet = get_db_worksheet("users")
    row = find_db_row(worksheet, chat_id=chat_id)

    if row is not None:
        worksheet.update(f"B{row}", [[email]])
    else:
        worksheet.append_row([chat_id, email, ""])


def save_user_sheet(chat_id: str, sheet_id: str) -> None:
    worksheet = get_db_worksheet("users")
    row = find_db_row(worksheet, chat_id=chat_id)

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


def get_sheet_id(
    email: str | None = None,
    chat_id: str | None = None
) -> Optional[str]:
    """Get a user's sheet ID using either email or chat_id."""

    if email is None and chat_id is None:
        return None

    if email is not None and email in _user_sheet_ids:
        return _user_sheet_ids[email]

    if chat_id is not None and chat_id in _telegram_chat_ids:
        return _telegram_chat_ids[chat_id]

    worksheet = get_db_worksheet("users")

    row = find_db_row(
        worksheet,
        email=email,
        chat_id=chat_id
    )

    if row is None:
        return None

    email = worksheet.cell(row, COL_EMAIL).value
    chat_id = worksheet.cell(row, COL_CHAT_ID).value
    sheet_id = worksheet.cell(row, COL_SHEET_ID).value

    if sheet_id:
        if email:
            _user_sheet_ids[email] = sheet_id

        if chat_id:
            _telegram_chat_ids[chat_id] = sheet_id

    return sheet_id


def get_chat_id(sheet_id: str) -> Optional[str]:
    '''Sheet_id -> Chat_id'''
    worksheet = get_db_worksheet("users")
    row = find_db_row(worksheet, sheet_id=sheet_id)

    if row is None:
        return None

    return worksheet.cell(row, COL_CHAT_ID).value
