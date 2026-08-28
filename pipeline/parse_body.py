import re
from bs4 import BeautifulSoup

from telegrambot.database import get_sheet_id
from telegrambot.sheets import get_categories


EXPENSE_BLOCK_PATTERN = (
    r"Date\s*&\s*Time:\s*(.+)\n"
    r"Amount:\s*(.+)\n"
    r"From:\s*(.+)\n"
    r"\sTo:\s*(.+)"
)

INCOME_BLOCK_PATTERN = (
    r"From:\s*(.+)\n"
    r"To:\s*(.+)"
)

INCOME_SENTENCE_PATTERN = (
    r"received\s+(.+?)\s+on\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+via\s+\w+\."
)


def clean_body(body: str) -> str:
    """Convert HTML email to plain text"""
    soup = BeautifulSoup(body, "html.parser")

    for br in soup.find_all("br"):
        br.replace_with("\n")

    text = soup.get_text()

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)

    return text.strip()


def get_expense_block(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None,
              "from": None, "to": None, "type": None}

    matched = re.search(EXPENSE_BLOCK_PATTERN, cleaned_body, re.IGNORECASE)
    if matched:
        result["date"] = matched.group(1).strip()
        result["amount"] = matched.group(2).strip()
        result["from"] = matched.group(3).strip()
        result["to"] = matched.group(4).strip()
        result["type"] = "Expense"

    return result


def get_income_block(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None,
              "from": None, "to": None, "type": None}

    received_matched = re.search(
        r"received\s+(.+?)\s+via\s+\w+\s+on\s+(.+?)\.",
        cleaned_body,
        re.IGNORECASE,
    )
    if received_matched:
        result["amount"] = received_matched.group(1).strip()
        result["date"] = received_matched.group(2).strip()

    from_to_matched = re.search(
        INCOME_BLOCK_PATTERN, cleaned_body, re.IGNORECASE)
    if from_to_matched:
        result["from"] = from_to_matched.group(1).strip()
        result["to"] = from_to_matched.group(2).strip()
    result["type"] = "Income"

    return result


def get_income_sentence(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None,
              "from": None, "to": None, "type": None}
    matched = re.search(INCOME_SENTENCE_PATTERN,
                        cleaned_body, re.IGNORECASE | re.DOTALL)
    if matched:
        result["amount"] = matched.group(1).strip()
        result["date"] = matched.group(2).strip()
        result["from"] = matched.group(3).strip()
        result["to"] = matched.group(4).strip()
        result["type"] = "Income"

    return result


def extract_fields(body: str) -> dict:
    '''Extract fields from body'''
    cleaned_body = clean_body(body)
    fields = get_expense_block(cleaned_body)

    for extractor in (get_income_block, get_income_sentence):
        if not any(field is None for field in fields.values()):
            break
        fallback = extractor(cleaned_body)
        for header in fields:
            if fields[header] is None:
                fields[header] = fallback[header]

    return fields


def get_fields(message_info: dict[str, str]) -> dict:
    """Get user email and categories, then merge them with the extracted fields."""
    # Message_info contains email, body, full_date

    # Fields contains date, amount, from, to, type
    fields = extract_fields(message_info['body'])

    fields['full_date'] = message_info['date']

    sheet_id = get_sheet_id(email=message_info['email'])
    fields['sheet_id'] = sheet_id

    expense_categories, income_categories = get_categories(sheet_id)

    fields['expense_categories'] = expense_categories
    fields['income_categories'] = income_categories

    return fields  # Returns date, amount, from, to, type, full_date, sheet_id, expense_categories, income_categories
