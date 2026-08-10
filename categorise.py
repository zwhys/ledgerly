from typing import Any
from openai import OpenAI
import json
from dotenv import load_dotenv

from extract import get_unread_and_mark_read
from parse_body import add_user_to_result

load_dotenv()


client = OpenAI()

EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Health",
    "Education",
    "Entertainment",
    "Reimbursed Expenses"
]

INCOME_CATEGORIES = [
    "Allowance",
    "Salary",
    "Bonus",
    "Reimbursedment"
]


def extract_communicator(result: dict) -> dict[str, Any]:
    recipient: str = result['to']
    sender: str = result['from']
    return {"recipient": recipient, "sender": sender}


def transaction_type(body: dict) -> str:
    transaction: str = body['transaction']
    return transaction


def classify(result: dict):
    if transaction_type(result) == "Expense":
        categories = EXPENSE_CATEGORIES
        merchant = extract_communicator(result)["recipient"]
    elif transaction_type(result) == "Income":
        categories = INCOME_CATEGORIES
        merchant = extract_communicator(result)["sender"]

    prompt = f"""Classify the following text into exactly one of these categories: {", ".join(categories)}.

           Return ONLY a JSON object in this exact format, nothing else:
           {{"category": "...", "confidence": "high|low"}}

           Text:
           {merchant}
           """

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt,
        text={
            "format": {
                "type": "json_object"
            }
        },
    )

    raw = response.output_text.strip()
    raw_out = json.loads(raw)

    if raw_out["category"] not in categories:
        raw_out["category"] = "Other"

    print(raw_out)
    return raw_out


# TODO: Allow user to choose own category through a telegram bot, decided using confidence level
# TODO: Add error handling (Mark as read only after classification is done)

if __name__ == "__main__":
    results_out = get_unread_and_mark_read()
    for result in results_out:
        result = add_user_to_result(result)
        if result.get('date') is None:
            continue
        classify(result)
        

##TODO: Deal with '[forwarding-noreply@google.com](mailto\:forwarding-noreply@google.com)'