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

RECEIVED_SENTENCE_PATTERN = (
    r"received\s+(.+?)\s+on\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+via\s+\w+\."
)


def extract_angle_brackets(text):
    match = re.search(r"<([^>]+)>", text)
    return match.group(1) if match else None


def add_user_to_result(result: dict[str, str]):
    body = extract_fields(result['body'])
    user_email = extract_angle_brackets(result['user'])
    body['user_email'] = user_email
    return body


def clean_body(body: str) -> str:
    return re.sub(r"\*+", "", body)


def extract_labeled_block(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None,
              "from": None, "to": None, "transaction": None}
    matched = re.search(BLOCK_PATTERN, cleaned_body, re.IGNORECASE)
    if matched:
        result["date"] = matched.group(1).strip()
        result["amount"] = matched.group(2).strip()
        result["from"] = matched.group(3).strip()
        result["to"] = matched.group(4).strip()
        result["transaction"] = "Expense"

    return result


def extract_received_transfer(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None,
              "from": None, "to": None, "transaction": None}

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
    result["transaction"] = "Income"

    return result


def extract_received_sentence(cleaned_body: str) -> dict:
    result = {"date": None, "amount": None,
              "from": None, "to": None, "transaction": None}
    matched = re.search(RECEIVED_SENTENCE_PATTERN,
                        cleaned_body, re.IGNORECASE | re.DOTALL)
    if matched:
        result["amount"] = matched.group(1).strip()
        result["date"] = matched.group(2).strip()
        result["from"] = matched.group(3).strip()
        result["to"] = matched.group(4).strip()
        result["transaction"] = "Income"

    return result


def extract_fields(body: str) -> dict:
    cleaned_body = clean_body(body)
    result = extract_labeled_block(cleaned_body)

    for extractor in (extract_received_transfer, extract_received_sentence):
        if not any(value is None for value in result.values()):
            break
        fallback = extractor(cleaned_body)
        for key in result:
            if result[key] is None:
                result[key] = fallback[key]

    return result


if __name__ == "__main__":
    results_out = get_unread_and_mark_read()

    with open("mailTemplates/results.txt", "w", encoding="utf-8") as file:
        for result in results_out:
            file.write(str(add_user_to_result(result)) + "\n")
