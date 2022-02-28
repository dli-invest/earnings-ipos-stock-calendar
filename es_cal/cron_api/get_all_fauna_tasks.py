# grab summary and date from command line arguments

# simple def main program that outputs summary and date from command line arguments
import os
from es_cal.cron_api.cron import make_event_from_data
import spacy
import dateparser
# from es_cal.cron_api.cron import make_event_from_data
from faunadb import client, query as q
from datetime import datetime

def main():
    FAUNA_SECRET = os.getenv("FAUNA_SECRET")
    fClient = client.FaunaClient(FAUNA_SECRET, domain="db.us.fauna.com")
    nlp = spacy.load("en_core_web_sm")
    documents = fClient.query(
        q.map_(
            q.lambda_("x", q.get(q.var("x"))),
            q.paginate(q.documents(q.collection("Article")), size=100000),
        )
    )

    for document in documents.get("data"):
        print(document)
        data = document.get("data")
        print(data)
        doc = nlp(document["data"]["title"])
        extracted_date = None
        extracted_title = document["data"]["title"]
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
            # ignore "dates" if they can be parsed as a number
            if ent.label_ == "DATE":
                try:
                    if ent.text in ["Today", "Tomorrow", "Yesterday", "Decade", "40-Year", "Friday", "Thursday", "Wednesday", "Tuesday", "Monday", "Sunday", "Saturday", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Last Year", "Next Week's"]:
                        continue

                    if "Week" in ent.text:
                        continue
                    if "year" in ent.text:
                        continue
                    if "Year" in ent.text:
                        continue

                    if "-" in ent.text:
                        continue
                    num = int(ent.text, 10)
                    pass
                except ValueError as e:
                    print(e)
                    # dont want the number to be parsed as a date
                    extracted_date = dateparser.parse(ent.text)
                    if extracted_date != None:
                        if extracted_date.strftime('%Y-%m-%d') == datetime.now().strftime('%Y-%m-%d'):
                            extracted_date = None
                            continue
                        break

        if extracted_date != None:
            print(extracted_date)
            fmt_date = extracted_date.strftime("%Y-%m-%d")
            make_event_from_data(extracted_title, fmt_date)
            extracted_date = None
            continue

        # Spacy matcher TODO
        # check if docs meet other criteria
        # send to discord channel for now
        # terms are
        # first|second|third|fourth quarter
        # year results
        # annual report
        # months ended
        # conference call and webcast


if __name__ == '__main__':
    # get command line args
    main()
