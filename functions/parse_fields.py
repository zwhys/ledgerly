from typing import Any
import re
from datetime import datetime


from categorise import categorise


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
        f"{full_date_dt.strftime('%H:%M:%S')} (SGT)"
    )  # TODO: Look at effect on overseas transitions


def parse_fields(fields: dict) -> dict:
    category_and_confidence = categorise(fields)
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


def parse_data(fields: dict) -> dict:
    data = parse_fields(fields)
    # data.pop("confidence")
    data.pop("user_email")
    return data
