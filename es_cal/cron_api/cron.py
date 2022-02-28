# grab summary and date from command line arguments

# simple def main program that outputs summary and date from command line arguments

import sys
from es_cal.gcal.main import make_event_in_gcal

def make_event_from_data(summary: str, date: str):
    # assert date is str in YYYY-MM-DD format
    if summary is None:
        print("Error: summary is None")
        sys.exit(1)
    if date is None:
        print("Error: date is None")
        sys.exit(1)

    # create event in google calendar using summary and date
    make_event_in_gcal(summary, date)

if __name__ == '__main__':
    # get command line args
    summary = sys.argv[1]
    date = sys.argv[2]
    make_event_from_data(summary, date)