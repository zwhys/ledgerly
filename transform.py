import re
from extract import get_unread_and_mark_read

BLOCK_PATTERN = (
    r"Date\s*&\s*Time:\s*(.+)\n"
    r"Amount:\s*(.+)\n"
    r"From:\s*(.+)\n"
    r"To:\s*(.+)"
)

FROM_TO_BLOCK_PATTERN = (
    r"From:\s*(.+)\n"
    r"To:\s*(.+)"
)


def clean_body(body: str) -> str:
    return re.sub(r"\*+", "", body)


def extract_labeled_block(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None, "from": None, "to": None}
    matched = re.search(BLOCK_PATTERN, cleaned_body, re.IGNORECASE)
    if matched:
        result["date"] = matched.group(1).strip()
        result["amount"] = matched.group(2).strip()
        result["from"] = matched.group(3).strip()
        result["to"] = matched.group(4).strip()
    return result


def extract_received_transfer(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None, "from": None, "to": None}

    received_matched = re.search(
        r"received\s+(.+?)\s+via\s+\w+\s+on\s+(.+?)\.",
        cleaned_body,
        re.IGNORECASE,
    )
    if received_matched:
        result["amount"] = received_matched.group(1).strip()
        result["date"] = received_matched.group(2).strip()

    from_to_matched = re.search(
        FROM_TO_BLOCK_PATTERN, cleaned_body, re.IGNORECASE)
    if from_to_matched:
        result["from"] = from_to_matched.group(1).strip()
        result["to"] = from_to_matched.group(2).strip()

    return result


def extract_fields(body: str) -> dict:
    cleaned_body = clean_body(body)

    result = extract_labeled_block(cleaned_body)

    if any(v is None for v in result.values()):
        fallback = extract_received_transfer(cleaned_body)
        for key in result:
            if result[key] is None:
                result[key] = fallback[key]

    return result


if __name__ == "__main__":
    bodies = get_unread_and_mark_read()
    for body in bodies:
        print(extract_fields(body))
