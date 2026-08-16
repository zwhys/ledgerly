from extract import get_all_message_info
from parse_body import get_fields
from parse_fields import parse_data
from sheets import append_transaction
from database import init_db, get_sheet_id_for_user


def main(event, context):
    init_db()
    all_message_info = get_all_message_info()

    for message_info in all_message_info:
        fields = get_fields(message_info)
        if fields.get('date') and fields.get('amount') is None:
            continue

        user_email = fields.get("user_email")
        sheet_id = get_sheet_id_for_user(user_email)
        # add_new_user(user_email, sheet_id) #TODO: Fix when telegram bot works

        if sheet_id is None:
            continue

        entry = parse_data(fields)
        append_transaction(sheet_id, entry)

    return {
        "statusCode": 200,
        "body": "Lambda SUCCESS"
    }


if __name__ == "__main__":
    # event = context = None
    # main(event, context)
    main()


# TODO: Optimise performance (promises and parallel processing)
