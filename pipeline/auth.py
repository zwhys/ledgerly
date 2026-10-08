import logging
import os

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        # scopes=SCOPES,
    )

    if not creds.valid:
        logging.info("Google credentials are invalid, refreshing token")

        try:
            creds.refresh(Request())
            logging.info("Google credentials refreshed successfully")

        except RefreshError as e:
            logging.error(
                "Google authentication failed. "
                "Please refresh your Google OAuth token and "
                "update GOOGLE_REFRESH_TOKEN."
            )
            raise RuntimeError(
                "Google refresh token is invalid. "
                "Please refresh your Google OAuth token and "
                "update GOOGLE_REFRESH_TOKEN."
            ) from e

    return creds
