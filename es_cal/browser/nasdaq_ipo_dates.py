import time
from es_cal.browser.browser import make_webdriver
import pandas as pd
from es_cal.discord import send_message
from datetime import datetime
print("STARTING SCRIPT")
nasdaq_url = "https://www.nasdaq.com/market-activity/ipos"
driver = make_webdriver("Get Nasdaq Ipos")
print("MAKING SELENIUM SCRIPT")
driver.get("https://www.google.com")
driver.get(nasdaq_url)
time.sleep(10)
print("DO SOMETHING SCRIPT")
page_source = driver.page_source

tables = pd.read_html(page_source, attrs={"class": "market-calendar-table__table"})
driver.close()

upcoming = tables[0]
priced = tables[1]
print(upcoming, priced)

# send discord messages for all the upcoming priced listings that 

upcoming.to_csv("artifacts/upcoming.csv")
priced.to_csv("artifacts/priced.csv")

# symbol, price, ipo date, offer amount

def mapIpoForDiscord(item: dict):
    date = item.get("Expected IPO Date")
    if date == None:
        try:
            date = item.get("Date")
        except Exception as e:
            date = "N/A"
    content = f"{item['Company Name']} {date}"
    embed = {
        'title': item["Symbol"],
        'description': f"{item['Company Name']}",
        'url': nasdaq_url,
        'fields': [
            {
                'name': "price",
                "value": item['Price'],
                "inline": True
            },
            {
                'name': "date",
                "value": date,
                "inline": True
            },
        ]
    }
    embeds = [embed]
    return content, embeds

for index, row in upcoming.iterrows():
    date = row.get("Expected IPO Date")
    if date == None:
        date = row.get("Date")
    parsedDate = datetime.strptime(date, "%m/%d/%Y")
    if (parsedDate - datetime.today()).days >= 1:
        content, embeds = mapIpoForDiscord(row)
        send_message(content, embeds)
        time.sleep(2)
else:
    send_message("[earnings-stock-calendar] - no ipos", [])
