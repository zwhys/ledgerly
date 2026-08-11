from typing import Any
from openai import OpenAI
import json
from dotenv import load_dotenv

EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Health",
    "Education",
    "Entertainment",
]

INCOME_CATEGORIES = [
    "Allowance",
    "Salary",
    "Bonus",
]

load_dotenv()
client = OpenAI()


def extract_communicator(fields: dict) -> dict[str, Any]:
    recipient: str = fields['to']
    sender: str = fields['from']
    return {"recipient": recipient, "sender": sender}


def transaction_type(fields: dict) -> str:
    type: str = fields['type']
    return type


def categorise(fields: dict) -> dict:
    '''Classifies the category and add the confidence level'''
    if transaction_type(fields) == "Expense":
        categories = EXPENSE_CATEGORIES
        merchant = extract_communicator(fields)["recipient"]
    elif transaction_type(fields) == "Income":
        categories = INCOME_CATEGORIES
        merchant = extract_communicator(fields)["sender"]

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

    category_and_confidence: str = json.loads(response.output_text.strip())

    if category_and_confidence["category"] not in categories:
        category_and_confidence["category"] = "Other"

    return category_and_confidence


# TODO: Allow user to choose own category through a telegram bot, decided using confidence level
# TODO: Add error handling (Mark as read only after classification is done)
