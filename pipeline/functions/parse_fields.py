from typing import Any
import re
from datetime import datetime

from categorise import categorise_all


def format_date(date: str, full_date: str) -> str:
    date_dt = datetime.strptime(
        date.replace(" (SGT)", ""),
        "%d %b %H:%M"
    )

    full_date_dt = datetime.strptime(
        full_date,
        "%a, %d %b %Y %H:%M:%S %z"
    )

    return (
        f"{date_dt.day:02d}/{date_dt.month:02d}/{full_date_dt.year} "
        f"{date_dt.strftime('%H:%M')}:{full_date_dt.second:02d} (SGT)"
    )  # TODO: Look at effect on overseas transitions


def parse_fields(fields: dict, category_and_confidence: dict) -> dict:
    '''Now takes the category/confidence as an argument instead of computing it itself'''
    match = re.match(r"([A-Za-z]+)\s*([\d.]+)", fields["amount"])

    data: dict[str, Any] = {
        "date": format_date(fields["date"], fields["full_date"]),
        "type": fields["type"],
        "category": category_and_confidence["category"],
        "amount": match.group(2),
        "currency": match.group(1),
        "confidence": category_and_confidence["confidence"],
        "user_email": fields["user_email"]
    }

    return data


def parse_data_all(fields: list[dict]) -> list[dict]:
    '''Batches categorisation in parallel, then parses each message using its result'''
    categories_and_confidences = categorise_all(fields)

    results = []
    for fields, category_and_confidence in zip(fields, categories_and_confidences):
        data = parse_fields(fields, category_and_confidence)
        # data.pop("confidence")
        data.pop("user_email")
        results.append(data)

    return results
