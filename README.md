# LedgerlyBot

Ledgerly is a Gmail-polling ETL pipeline that categorizes **DBS** bank transactions via an LLM and stores them in Google Sheets

## Features

## Setup

### 1. Import Gmail Filters

Download `mailFilters.xml` and import it into Gmail:

1. Go to [Gmail](https://mail.google.com/).
2. Click **Settings** → **See all settings**.
3. Go to **Filters and Blocked Addresses**.
4. Click **Import filters**.
5. Import `mailFilters.xml`

### 2. Create a Google Sheet

Create a new Google Spreadsheet. The spreadsheet name and worksheet name do not matter.

Share the spreadsheet with the following service account and give it **Editor** permissions:

`ledgerlybot@ledgerly-505005.iam.gserviceaccount.com`

### 3. Share the Google Sheet URL

Email tanziyan297@gmail.com the URL of the google sheet

<!-- TODO: Find a better way  -->

### 4. Done

That's all you need to do. Ledgerly is now ready to use.

## How It Works

1. **Email Processing** — Ledgerly polls the bot's Gmail inbox via OAuth,
   retrieves unread emails, extracts the sender's address and email body, and
   marks them as read.

2. **Transaction Extraction** — Regex parses the email body for amount,
   transaction type, date, sender, and recipient.

3. **Categorisation** — Extracted data is sent to an LLM, which assigns
   a category and confidence score.

4. **Recording** — The combined record is written as a new row in the
   user's connected Google Sheet.

_Requires Gmail filters and Sheet access to be configured first — see [Setup](##setup)._

## Built With

## Future Improvements

<!-- Also known as limitations -->

1.  Add support for other banks (Only supports DBS banks for now)
