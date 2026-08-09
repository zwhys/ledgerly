import pprint
from extract import get_unread_and_mark_read

def transform(bodies: list[str]):
    pprint.pprint(bodies)
    return

if __name__ == '__main__':
    transform(get_unread_and_mark_read())