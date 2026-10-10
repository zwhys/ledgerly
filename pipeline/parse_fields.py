import logging
from typing import Any
import re
from datetime import datetime
import uuid

from categorise import categorise_all


def format_date(date: str, full_date: str) -> str:
    """Formats date as DD/MM/YYYY HH:MM (SGT)."""

    full_date = full_date.strip()

    if full_date.endswith(" SGT"):
        full_date = full_date[:-4]

    year = datetime.strptime(
        full_date,
        "%a, %d %b %Y %H:%M:%S %z"
    ).year

    date = date.strip().replace(" (SGT)", "")

    date_dt = datetime.strptime(
        date,
        "%d %b %Y %H:%M"
    ) if len(date.split()) == 4 else datetime.strptime(
        date,
        "%d %b %H:%M"
    ).replace(year=year)

    formatted = date_dt.replace(year=year)

    return formatted.strftime("%d/%m/%Y %H:%M (SGT)")

    # TODO: Look at effect on overseas transitions


def parse_fields(fields: dict, category: str) -> dict:
    '''Now takes the category/confidence as an argument instead of computing it itself'''
    amount = fields.get("amount")

    if not amount:
        logging.error("Missing amount: fields=%s", fields)
        return None

    # TODO: Fix the regex for overseas transactions
    match = re.match(r"(S\$|[A-Za-z]{3})\s*([\d.]+)", amount)

    if not match:
        logging.error("Invalid amount format: %s", amount)
        return None

    currency = match.group(1)

    if currency == "S$":
        currency = "SGD"

    # Returns date, amount, from, to, type, full_date, sheet_id, expense_categories, income_categories
    # Data is date, type, category, amount, currency

    entry: dict[str, Any] = {
        "date": format_date(fields["date"], fields["full_date"]),
        "type": fields["type"],
        "category": category,
        "amount": match.group(2),
        "currency": currency,
        "sheet_id": fields["sheet_id"],
        "transaction_id": str(uuid.uuid4())[-12:]
    }

    logging.info('Entry: %s', entry)

    return entry


def parse_data_all(list_of_fields: list[dict]) -> list[dict]:
    '''Batches categorisation in parallel, then parses each message using its result'''
    categories = categorise_all(list_of_fields)

    entries = []
    for list_of_fields, category in zip(list_of_fields, categories):
        data = parse_fields(list_of_fields, category)
        entries.append(data)

    return entries
