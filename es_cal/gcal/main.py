"""A simple example of how to access the Google Analytics API."""

# 1. Create a dictionary with the event data
# 2. Create a service object with the credentials
# 3. Call the calendar API
# 4. Add the event to the calendar
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import date
from es_cal.gcal.utils import decode_json
from es_cal.gcal.config import scopes as gscopes, calendarId as gcalendarId

def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """
    credentials = service_account.Credentials.from_service_account_file(
        key_file_location, scopes=scopes
    )

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)
    print("Making service")
    return service


def make_calendar_service(service_file_path="stocks.json"):
    # Define the auth scopes to request.
    key_file_location = service_file_path
    scopes = gscopes
    # Authenticate and construct service.
    service = get_service(
        api_name="calendar",
        api_version="v3",
        scopes=scopes,
        key_file_location=key_file_location,
    )
    return service


def make_event_data(summary, date=date.today(), email="davidli012345@gmail.com"):
    # Only thing I get from trading view is date, so append timezone to inputted date
    start_date = f"{date}T05:30:00-07:00"
    end_date = f"{date}T07:00:00-07:00"
    return {
        "summary": summary,
        "start": {
            "dateTime": start_date,
            "timeZone": "America/Vancouver",
        },
        "end": {
            "dateTime": end_date,
            "timeZone": "America/Vancouver",
        },
        "reminders": {
            "useDefault": True,
        },
    }


def check_if_event_exists(service, new_summary):
    """
    Description: checks if the event summary exists using a naive approach
    """
    event_exists = False
    page_token = None
    calendarId = gcalendarId
    while True:
        events = (
            service.events().list(calendarId=calendarId, pageToken=page_token).execute()
        )
        for event in events["items"]:
            # purge location from summary string
            if new_summary in event["summary"]:
                event_exists = True
                break
        page_token = events.get("nextPageToken")
        if not page_token:
            break
    return event_exists


def make_event_in_gcal(event_name, date):
    """
    Input:
        event_name: string
        date: YYYY-MM-DD formatted string
    Output:
        adds an new event or does nothing
    """
    decode_json()
    service = make_calendar_service()
    calendarId = gcalendarId
    if check_if_event_exists(service, event_name):
        print(f"{event_name} exists already, not creating event")
        return False
    else:
        event_data = make_event_data(event_name, date)
        print(event_data)
        event = (
            service.events().insert(calendarId=calendarId, body=event_data).execute()
        )
        print("Event created: %s" % (event.get("htmlLink")))
        return True


def main():
    decode_json()
    service = make_calendar_service()
    calendarId = gcalendarId
    event_name = "NTAR May Earnings"
    if check_if_event_exists(service, event_name):
        print(f"{event_name} exists already, not creating event")
    else:
        event_data = make_event_data(event_name, "2020-05-14")
        event = (
            service.events().insert(calendarId=calendarId, body=event_data).execute()
        )
        print("Event created: %s" % (event.get("htmlLink")))


if __name__ == "__main__":
    main()
