import os
import base64
from typing import Any
from google.auth.transport.requests import AuthorizedSession
from auth import get_credentials


ENV = os.getenv("ENV", "dev")

if ENV == "dev":
    from dotenv import load_dotenv
    load_dotenv()

GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"


def get_response(session: AuthorizedSession) -> dict:
    response = session.get(
        f"{GMAIL_API}/messages",
        params={"q": "is:unread"},
    )

    response.raise_for_status()
    return response.json()


def mark_emails_as_read(
    session: AuthorizedSession,
    response_message_ids: list[str],
) -> None:
    """Mark all specified emails as read."""

    if not response_message_ids:
        return

    response = session.post(
        f"{GMAIL_API}/messages/batchModify",
        json={
            "ids": response_message_ids,
            "removeLabelIds": ["UNREAD"],
        },
    )

    response.raise_for_status()


def parse_message(full_message: dict[str, Any]) -> dict[str, str]:
    message_payload = full_message.get("payload", {})
    payload_parts = message_payload.get("parts", [])
    payload_headers = message_payload.get("headers", [])

    email = ""
    full_date = ""

    for header in payload_headers:
        if header["name"] == "Delivered-To":
            email = header["value"]
        elif header["name"] == "Date":
            full_date = header["value"]

    body = ""

    for part in payload_parts:
        if part.get("mimeType") == "text/html":
            data = part.get("body", {}).get("data", "")

            if data:
                body = base64.urlsafe_b64decode(data).decode("utf-8")

            break

    return {
        "email": email,
        "body": body,
        "date": full_date,
    }


def get_message_info(
    session: AuthorizedSession,
    message_id: str,
) -> dict[str, str]:
    """Get the user email, body, and date of one email."""

    response = session.get(
        f"{GMAIL_API}/messages/{message_id}",
        params={"format": "full"},
    )

    response.raise_for_status()

    full_message = response.json()

    return parse_message(full_message)


def get_all_message_info() -> list[dict[str, str]]:
    """Get the user email, body, and date of all unread emails."""

    creds = get_credentials()
    session = AuthorizedSession(creds)

    response = get_response(session)

    response_messages: list[dict[str, str]] = response.get("messages", [])
    response_messages.reverse()  # Get the messages in chronological order

    all_message_info: list[dict[str, str]] = []
    response_message_ids: list[str] = []

    for message in response_messages:
        message_id = message["id"]

        message_info = get_message_info(
            session,
            message_id,
        )

        all_message_info.append(message_info)
        response_message_ids.append(message_id)

    if ENV == "prod":
        mark_emails_as_read(
            session,
            response_message_ids,
        )
    return all_message_info
