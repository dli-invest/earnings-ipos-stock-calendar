# grab summary and date from command line arguments

# simple def main program that outputs summary and date from command line arguments
import os
import re
from es_cal.cron_api.cron import make_event_from_data
from es_cal.discord.notify import send_message
import spacy
import time
import dateparser
# from es_cal.cron_api.cron import make_event_from_data
from faunadb import client, query as q
from datetime import datetime
import os
import psycopg

def insert_row_to_db(doc, extracted_date):
    """
    doc from fauna db instance, likely a bunch of data missing
    """
    data = doc["data"]
    conn_dict =  psycopg.conninfo.conninfo_to_dict(os.environ["COCKROACH_DB_URL"])
    #     conn.execute("CREATE TABLE events (date date, title text, description text, source text, country text, exchange text, url text, company text)")
    title = data.get("title", "")
    description = data.get("description", "")
    source = data.get("source", "faunadb")
    country = data.get("country", "us")
    exchange = data.get("exchange", "")
    company = data.get("company", "")
    url = data.get("url", "")
    print("ATTEMPT TO INSERT VALUES")
    with psycopg.connect(**conn_dict) as conn:
        conn.execute("INSERT INTO events VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (extracted_date, title, description, source, country, exchange, url, company))
    print("WHAT IS GOING ON HERE")

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

    transcript_docs = []
    for document in documents.get("data"):
        data = document.get("data")
        doc = nlp(document["data"]["title"])
        extracted_date = None
        extracted_title = document["data"]["title"]
        multiword_list  = ["next week's", "simply wall", "three years", "zacks", "virtual investor conference", "motley fool", "roadshow series", "institutional investors conference", "speak at"]
            # check if extracted_title has any substrings in multiword list
        pattern = re.compile(r'\b(?:' + '|'.join(re.escape(s) for s in multiword_list) + r')\b')
        matches = pattern.findall(extracted_title.lower())
        if len(matches) > 0:
            print(matches)
            print(extracted_title)
            continue
        for ent in doc.ents:
            # ignore "dates" if they can be parsed as a number
            if ent.label_ == "DATE":
                try:
                    if ent.text.lower() in ["today", "tomorrow", "yesterday", "decade", "40-year", "friday", "thursday", "wednesday", "tuesday", "monday", "sunday", "saturday", "january", "February", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "last year", "next week's", "week", "-", "zacks", "roadshow", "participate", "convention"]:
                        continue
                    # check ent.text in multiword list contains
                    num = int(ent.text, 10)

                except ValueError as e:
                    # print(e)
                    # dont want the number to be parsed as a date
                    extracted_date = dateparser.parse(ent.text)
                    if extracted_date != None:
                        if extracted_date.strftime('%Y-%m-%d') == datetime.now().strftime('%Y-%m-%d'):
                            extracted_date = None
                            continue
                        break

        if extracted_date != None:
            try:
                insert_row_to_db(doc, extracted_date)
                print("SUCCESSFULLY ADDED ROW TO COCKROACH DB")
            except Exception as e:
                print(e)
                print("FAILED TO CREATE EVENT")
            # re.IGNORECASE
            # make sure its an earnings call
            # must contain word quarter, results, annual report or months ended
            fmt_date = extracted_date.strftime("%Y-%m-%d")
            new_event = make_event_from_data(extracted_title, fmt_date)
            if new_event:
                send_message(extracted_title, [])
                time.sleep(2)
            extracted_date = None
            # send to discord
            continue

        # Spacy matcher TODO
        # might move this funcitonality to the latex report I will likely be generating
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
