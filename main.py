from extract import get_users_and_bodies
from parse_body import get_user_email_addr_and_fields
from parse_fields import parse_data
from sheets import append_transaction, add_new_user
from store import init_db, get_sheet_id_for_user


if __name__ == "__main__":
    init_db()
    users_and_bodies = get_users_and_bodies()

    for user_and_body in users_and_bodies:
        fields = get_user_email_addr_and_fields(user_and_body)
        if fields.get('date') and fields.get('amount') is None:
            continue

        user_email = fields.get("user_email")
        sheet_id = get_sheet_id_for_user(user_email)
        add_new_user(user_email, sheet_id)

        if sheet_id is None:
            continue

        entry = parse_data(fields)
        append_transaction(sheet_id, entry)


#TODO: Telegram bot
#TODO: 1. Allow user to choose own category
#TODO: 2. Allow user to create their own categories
#TODO: 3. Use this to give the sheets url
