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


def transaction_type(fields: dict) -> str:
    type: str = fields['type']
    return type


def categorise(fields: dict) -> dict:
    """Classifies the category and adds the confidence level."""

    transaction = transaction_type(fields)

    if transaction == "Expense":
        categories = fields["expense_categories"]
        merchant = extract_communicator(fields)["recipient"]

    elif transaction == "Income":
        categories = fields["income_categories"]
        merchant = extract_communicator(fields)["sender"]

    else:
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

    return result.model_dump()  # model_dump converts it to a dict


def categorise_all(fields_list: list[dict], max_workers: int = 5) -> list[dict]:
    '''Runs categorise() over all messages in parallel, preserving order'''
    # Allow for the messages to be returned in order
    categories_and_confidences = [None] * len(fields_list)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_mappings = {
            executor.submit(categorise, fields): i for i, fields in enumerate(fields_list)
        }  # Creates a map between a future and its message index

        for future in as_completed(future_mappings):
            i = future_mappings[future]
            try:
                categories_and_confidences[i] = future.result()
            except Exception as e:
                categories_and_confidences[i] = {"category": "Other",
                                                 "confidence": "low", "error": str(e)}

    return categories_and_confidences
