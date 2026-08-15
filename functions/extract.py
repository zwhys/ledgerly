import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import base64
from typing import Any

from auth import get_credentials

load_dotenv()

ENV = os.getenv("ENV", "dev")


def get_response(service) -> dict[str, Any]:
    '''Get unread emails'''
    response: dict[str, Any] = service.users().messages().list(
        userId='me', q='is:unread').execute()
    return response


def mark_emails_as_read(service, response_message_ids):
    service.users().messages().batchModify(
        userId='me',
        body={
            'ids': response_message_ids,
            'removeLabelIds': ['UNREAD']
        }
    ).execute()
    return


def parse_message(full_message: dict[str, str]) -> dict[str, str]:
    message_payload: dict[str, Any] = full_message.get('payload', {})
    payload_parts: list[dict] = message_payload.get('parts', [])
    payload_headers: list[dict] = message_payload.get('headers', [])

    user_email = ''
    full_date = ''

    for header in payload_headers:
        if header['name'] == 'Delivered-To':
            user_email = header['value']
        elif header['name'] == 'Date':
            full_date = header['value']

    body = ''

    for part in payload_parts:
        if part['mimeType'] == 'text/html':
            data = part['body'].get('data', '')
            body = base64.urlsafe_b64decode(data).decode('utf-8')
            break

    return {
        'user_email': user_email,
        'body': body,
        'date': full_date
    }


def get_message_info(service, message_id: str) -> dict[str, str]:
    """Get the user email, body, and date of one email."""
    full_message = service.users().messages().get(
        userId='me',
        id=message_id
    ).execute()

    message_info = parse_message(full_message)

    return message_info


def get_all_message_info() -> list[dict[str, str]]:
    """Get the user email, body, and date of all unread emails."""

    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    response = get_response(service)

    response_messages: list[dict[str, str]] = response.get('messages', [])
    all_message_info: list[dict[str, str]] = []
    response_message_ids: list[str] = []

    for message in response_messages:
        message_info = get_message_info(service, message['id'])
        all_message_info.append(message_info)

    if ENV == "prod":
        mark_emails_as_read(service, response_message_ids)

    return all_message_info


# TODO: Make it so that it runs everytime there is a new email being forwarded into the inbox
