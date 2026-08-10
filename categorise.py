from typing import Any
from openai import OpenAI
import json
from parse_body import extract_fields

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


def extract_communicator(body: dict) -> dict[str, Any]:
   recipient: str = body['to']
   sender: str = body['from']
   return {"recipient": recipient, "sender": sender}


def transaction_type(body: dict) -> str:
   transaction: str = body['transaction']
   return transaction


def classify(merchant: str):
   if transaction_type() == "Expense":
       categories = EXPENSE_CATEGORIES
   else:
       categories = INCOME_CATEGORIES
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
   result = json.loads(raw)

   if result["category"] not in categories:
       result["category"] = "Other"

   return result


# TODO: Allow user to choose own category through a telegram bot, decided using confidence level
# TODO: Add error handling (Mark as read only after classification is done)

# if __name__ == "__main__":

