from extract import get_all_message_info
from parse_body import get_fields
from parse_fields import parse_data_all
from sheets import append_transaction
from database import get_sheet_id_for_user
import time


def main(event, context):
    all_message_info = get_all_message_info()

    to_be_categorised: list[tuple] = []  # list of (fields, sheet_id) tuples

    for message_info in all_message_info:
        fields = get_fields(message_info)
        # print("FIELDS:", fields)
        # Test prints

        if fields.get('date') and fields.get('amount') is None:
            continue

        # print("PASSED VALIDATION")
        # Test prints

        email = fields.get("email")
        # print("EMAIL:", email)
        # Test prints

        sheet_id = get_sheet_id_for_user(email)
        # print("SHEET ID:", sheet_id)
        # Test prints

        if sheet_id is None:
            # print("SKIPPED: no sheet_id")
            # Test prints
            continue

        to_be_categorised.append((fields, sheet_id))
        # print("TO BE CATEGORISED:", to_be_categorised)
        # Test prints

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
