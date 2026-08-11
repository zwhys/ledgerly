import re

EXPENSE_BLOCK_PATTERN = (
    r"Date\s*&\s*Time:\s*(.+)\n"
    r"Amount:\s*(.+)\n"
    r"From:\s*(.+)\n"
    r"To:\s*(.+)"
)

INCOME_BLOCK_PATTERN = (
    r"From:\s*(.+)\n"
    r"To:\s*(.+)"
)

INCOME_SENTENCE_PATTERN = (
    r"received\s+(.+?)\s+on\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+via\s+\w+\."
)


def clean_body(body: str) -> str:
    '''Remove any markdown characters'''
    return re.sub(r"\*+", "", body)


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


def get_fields(body: str) -> dict:
    cleaned_body = clean_body(body)
    fields = get_expense_block(cleaned_body)

    for extractor in (get_income_block, get_income_sentence):
        if not any(field is None for field in fields.values()):
            break
        fallback = extractor(cleaned_body)
        for key in fields:
            if fields[key] is None:
                fields[key] = fallback[key]

    return fields


# TODO: Make sure this works as intended (No mailto links) like '[forwarding-noreply@google.com](mailto\:forwarding-noreply@google.com)'
def get_email_addr(text):
    match = re.search(r"<([^>]+)>", text)
    return match.group(1) if match else None


def get_user_email_addr_and_fields(user_and_body: dict[str, str]):
    '''Get user email address from user and merge it with fields'''
    body = user_and_body['body']
    user = user_and_body['user']
    fields = get_fields(body)
    user_email = get_email_addr(user)
    fields['user_email'] = user_email
    return fields
