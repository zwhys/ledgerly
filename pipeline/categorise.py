import os
from typing import Any, Literal
from pydantic import BaseModel
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed


ENV = os.getenv("ENV", "dev")

if ENV == "dev":
    from dotenv import load_dotenv
    load_dotenv()

client = OpenAI()


class CategoryResponse(BaseModel):
    category: str
    confidence: Literal["high", "low"]


def extract_communicator(fields: dict) -> dict[str, Any]:
    recipient: str = fields['to']
    sender: str = fields['from']
    return {"recipient": recipient, "sender": sender}


def categorise(fields: dict) -> str:
    """Classifies the category"""

    transaction = str(fields['type'])
    communicator = extract_communicator(fields)

    if transaction == "Expense":
        categories = fields["expense_categories"]
        merchant = communicator["recipient"]

    elif transaction == "Income":
        categories = fields["income_categories"]
        merchant = communicator["sender"]

    else:  # Failsafe unlikely to trigger, may trigger in the future if how transaction type is identified
        return {"category": "Other", "confidence": "low"}

    prompt = f"""
            Classify the following merchant into exactly one of these categories:

            {", ".join(categories)}

            Merchant:
            {merchant}
            """

    response = client.responses.parse(
        model="gpt-4.1-nano",
        input=prompt,
        text_format=CategoryResponse,
    )

    result = response.output_parsed

    if result.confidence == "low" or result.category not in categories:
        result.category = "Other"

    return result.category


def categorise_all(list_of_fields: list[dict], max_workers: int = 5) -> list[str]:
    '''Runs categorise() over all messages in parallel, preserving order'''
    # Allow for the messages to be returned in order
    categories = [None] * len(list_of_fields)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_mappings = {
            executor.submit(categorise, fields): i for i, fields in enumerate(list_of_fields)
        }  # Creates a map between a future and its message index

        for future in as_completed(future_mappings):
            i = future_mappings[future]
            try:
                categories[i] = future.result()
            except Exception as e:
                # TODO: Take a look at how to handle the exception
                categories[i] = {"category": "Other", "error": str(e)}

    return categories
