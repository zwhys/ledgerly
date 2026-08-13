from googleapiclient.discovery import build
import base64
from typing import Any

from auth import get_credentials


def get_response(service) -> dict[str, Any]:
    '''Get unread emails'''
    # response: dict[str, Any] = service.users().messages().list(
    #     userId='me', q='is:unread').execute() #!for production
    response: dict[str, Any] = service.users().messages().list(
        userId='me').execute()  # !for testing
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


def get_users_and_bodies() -> list[dict[str, str]]:
    '''Get user of service and body of email of all unread emails'''
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    response = get_response(service)
    response_messages: list[dict[str, str]] = response.get('messages', [])

    response_message_ids: list[str] = []
    users_and_bodies: list[dict[str, str]] = []

    for message in response_messages:
        full_message = service.users().messages().get(
            userId='me', id=message['id']).execute()

        message_payload: dict[str, Any] = full_message.get('payload', {})
        payload_parts: list[dict] = message_payload.get('parts', [])
        payload_headers: list[dict] = message_payload.get('headers', [])

        user = ''
        full_date = ''
        for header in payload_headers:
            if header['name'] == 'From':
                user = header['value']
            if header['name'] == 'Date':
                full_date = header['value']
            

        body = ''
        for msg_data_part in payload_parts:
            if msg_data_part['mimeType'] == 'text/plain':
                data = msg_data_part['body'].get('data', '')
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                break

        users_and_bodies.append({'user': user, 'body': body, 'date': full_date})
        response_message_ids.append(message['id'])

    mark_emails_as_read(service, response_message_ids)
    return users_and_bodies

# TODO: Make it so that it runs everytime there is a new email being forwarded into the inbox
