from googleapiclient.discovery import build
import base64
from typing import Any
from auth import get_credentials


def get_unread_and_mark_read() -> list[str]:
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    # results: dict[str, Any] = service.users().messages().list(
    #     userId='me', q='is:unread').execute() #!for production
    results: dict[str, Any] = service.users().messages().list(
        userId='me').execute()  # !for testing
    messages: list[dict[str, str]] = results.get('messages', [])

    message_ids: list[str] = []
    bodies: list[str] = []

    for msg in messages:
        full_msg = service.users().messages().get(
            userId='me', id=msg['id']).execute()

        payload: dict[str, Any] = full_msg['payload']
        parts: list[dict] = payload.get('parts', [])

        for msg_data_part in parts:
            if msg_data_part['mimeType'] == 'text/plain':
                data = msg_data_part['body'].get('data', '')
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                bodies.append(body)
                break

        message_ids.append(msg['id'])

    service.users().messages().batchModify(
        userId='me',
        body={
            'ids': message_ids,
            'removeLabelIds': ['UNREAD']
        }
    ).execute()

    return bodies


if __name__ == '__main__':
    get_unread_and_mark_read()


#TODO: Make it so that it runs everytime there is a new email being forwarded into the 