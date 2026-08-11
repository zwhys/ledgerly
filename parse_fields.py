from typing import Any
import re

from categorise import categorise


def parse_fields(fields: dict) -> dict:
    category_and_confidence = categorise(fields)
    match = re.match(r"([A-Za-z]+)\s*([\d.]+)", fields["amount"])

    data: dict[str, Any] = {
        "date": fields["date"],
        "type": fields["type"],
        "category": category_and_confidence["category"],
        "amount": match.group(2),
        "currency": match.group(1),
        "confidence": category_and_confidence["confidence"],
        "user_email": fields["user_email"]
    }

    return data
