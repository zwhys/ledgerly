from googleapiclient.discovery import build
import re
import base64
from typing import Any
from auth import get_credentials


def get_unread_and_mark_read() -> list[dict[str, str]]:
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    # results: dict[str, Any] = service.users().messages().list(
    #     userId='me', q='is:unread').execute() #!for production
    results: dict[str, Any] = service.users().messages().list(
        userId='me').execute()  # !for testing
    messages: list[dict[str, str]] = results.get('messages', [])

    message_ids: list[str] = []
    results_out: list[dict[str, str]] = []

    for msg in messages:
        full_msg = service.users().messages().get(
            userId='me', id=msg['id']).execute()

        payload: dict[str, Any] = full_msg.get('payload', {})
        parts: list[dict] = payload.get('parts', [])
        headers: list[dict] = payload.get('headers', [])

        user = ''
        for header in headers:
            if header['name'] == 'From':
                user = header['value']
                break

        body = ''
        for msg_data_part in parts:
            if msg_data_part['mimeType'] == 'text/plain':
                data = msg_data_part['body'].get('data', '')
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                break

        results_out.append({'user': user, 'body': body})
        message_ids.append(msg['id'])

    service.users().messages().batchModify(
        userId='me',
        body={
            'ids': message_ids,
            'removeLabelIds': ['UNREAD']
        }
    ).execute()
    return results_out

# TODO: Make it so that it runs everytime there is a new email being forwarded into the
