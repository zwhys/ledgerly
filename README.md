# Ledgerly

Ledgerly is a personal-finance ETL pipeline that reads DBS transaction alert emails from Gmail, extracts transaction details, uses an LLM to categorise transactions, and sends them to a Telegram bot for user vetting before recording them in Google Sheets. Users can also manually add transactions through the Telegram bot.

## Setup

### 1. Clone the Repository

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/zwhys/ledgerly.git

cd ledgerly
```

### 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the required environment variables:

```env
OPENAI_API_KEY=your_openai_api_key

GOOGLE_REFRESH_TOKEN=your_google_refresh_token
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_SERVICE_ACCOUNT=your_google_service_account_json

DB_SPREADSHEET_ID=your_database_spreadsheet_id

TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_NAME=your_telegram_bot_name
```

Do not commit `.env` or any credential files to the repository.

### 5. Configure Google APIs

Enable the following APIs in your Google Cloud project:

* Gmail API
* Google Sheets API

Configure the required OAuth credentials and service account credentials.

### 6. Import Gmail Filters

Download `mailFilters.xml` and import it into the Gmail account used by Ledgerly:

1. Open [Gmail](https://mail.google.com/).
2. Go to **Settings → See all settings**.
3. Open **Filters and Blocked Addresses**.
4. Click **Import filters**.
5. Select `mailFilters.xml` and import the filters.

These filters ensure that relevant DBS transaction emails are processed by Ledgerly.

### 7. Configure Google Sheets

Create a Google Spreadsheet to act as Ledgerly's database.

Set its ID as `DB_SPREADSHEET_ID` in the `.env` file and share the spreadsheet with the configured Google service account with **Editor** permissions.

User transaction spreadsheets should also be shared with the configured service account so Ledgerly can record transactions.

### 8. Run the Telegram Bot

Start the Telegram bot:

```bash
python -m telegrambot.main
```

### 9. Run the Transaction Pipeline

Start the transaction processing pipeline:

```bash
python -m pipeline.main
```

Ledgerly is now ready to use.

## How It Works

Ledgerly supports two ways of recording transactions:

1. **Automatic transactions** — DBS transaction emails are processed, categorised by an LLM, and sent to the user for vetting.
2. **Manual transactions** — Users can manually enter transactions through the Telegram bot.

### Automatic Transaction Pipeline

```text
DBS Transaction Email
        ↓
Sent to Ledgerly Inbox
        ↓
  Email Processing
        ↓
Transaction Extraction
        ↓
LLM Categorisation
        ↓
  User Vetting
        ↓
  Google Sheets
```

### 1. Email Processing

Ledgerly polls the Gmail inbox via OAuth, retrieves unread transaction emails, extracts the sender's address and email body, and marks processed emails as read.

### 2. Transaction Extraction

Regular expressions are used to extract structured transaction data from the email body, including:

* Amount
* Transaction type
* Date
* Sender
* Recipient

### 3. Categorisation

The extracted transaction data is sent to an LLM, which assigns an appropriate category to the transaction.

### 4. User Vetting

The categorised transaction is sent to the user through the Telegram bot.

The user can:

* Accept the transaction
* Reject the transaction
* Edit the transaction before recording it

This allows users to verify and correct the LLM's output before it is stored.

### 5. Manual Transactions

Users can manually add transactions directly through the Telegram bot using the **Add transaction** option.

The bot prompts the user to provide the transaction details, including:

* Date
* Transaction type
* Category
* Amount and currency
* Description

The transaction is then recorded in the user's Google Sheet without requiring a DBS transaction email or LLM categorisation.

### 6. Recording

Once a transaction has been approved or manually entered, Ledgerly writes the final transaction record to the user's Google Sheet.

## Future Improvements

* Support banks other than DBS
