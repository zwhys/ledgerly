from extract import get_all_message_info
from parse_body import get_fields
from parse_fields import parse_data_all
from sheets import append_transaction
from database import get_db_worksheet, get_sheet_id_for_user
import time


def main(event, context):
    get_db_worksheet()  # Works as db initialisation
    all_message_info = get_all_message_info()

    to_be_categorised: list[tuple] = []  # list of (fields, sheet_id) tuples

    for message_info in all_message_info:
        fields = get_fields(message_info)
        if fields.get('date') and fields.get('amount') is None:
            continue

        user_email = fields.get("user_email")
        sheet_id = get_sheet_id_for_user(user_email)

        if sheet_id is None:
            continue

        to_be_categorised.append((fields, sheet_id))

    if to_be_categorised:
        fields_list = [fields for fields, _ in to_be_categorised]
        entries = parse_data_all(fields_list)

        # Re-pair each parsed entry with its original sheet_id (order preserved from parse_data_all)
        for (fields, sheet_id), entry in zip(to_be_categorised, entries):
            append_transaction(sheet_id, entry)
            # pass

    return {
        "statusCode": 200,
        "body": "Lambda SUCCESS"
    }


if __name__ == "__main__":
    event = context = None
    start_time = time.time()
    main(event, context)
    print("--- %s seconds ---" % (time.time() - start_time))
    # main()
