from extract import get_all_message_info
from parse_body import get_fields
from parse_fields import parse_data_all
from sheets import append_transaction
import time


def main(event, context):
    all_message_info = get_all_message_info()

    list_of_fields: list = []

    for message_info in all_message_info:
        # Returns date, amount, from, to, type, full_date, sheet_id, expense_categories, income_categories
        fields = get_fields(message_info)

        # print("FIELDS:", fields)
        # Test prints

        if fields.get('date') and fields.get('amount') is None:
            continue

        sheet_id = fields.get("sheet_id")

        # print("SHEET ID:", sheet_id)
        # Test prints

        if sheet_id is None:
            continue

        list_of_fields.append(fields)

    if list_of_fields:
        entries = parse_data_all(list_of_fields)
        # print("ENTRIES:", entries)
        # Test prints

        for entry in entries:
            append_transaction(entry)

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
