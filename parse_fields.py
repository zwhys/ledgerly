from typing import Any
import re

from categorise import categorise
from extract import get_users_and_bodies
from parse_body import get_user_email_addr_and_fields


def parse_fields(fields: dict) -> dict:
    category_and_confidence = categorise(fields)
    match = re.match(r"([A-Za-z]+)\s*([\d.]+)", fields["amount"])

    data: dict[str, Any] = {
        "date": fields["date"],
        "transaction": fields["transaction"],
        "category": category_and_confidence["category"],
        "amount": match.group(2),
        "currency": match.group(1),
        "confidence": category_and_confidence["confidence"],
    }

    return data


if __name__ == "__main__":
    users_and_bodies = get_users_and_bodies()
    for user_and_body in users_and_bodies:
        fields = get_user_email_addr_and_fields(user_and_body)
        if fields.get('date') is None:
            continue
        print(parse_fields(fields))
