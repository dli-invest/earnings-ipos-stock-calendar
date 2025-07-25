import requests
from bs4 import BeautifulSoup
import pandas as pd
from icecream import ic
import datetime
from es_cal.gcal import make_event_in_gcal
from es_cal.discord import send_message
from es_cal.browser.googleSearch import searchGoogle, mapItemForDiscord

def convert_ipo_date(date: str):
    return datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')

def fetch_ipos(marketwatch_url = "https://www.marketwatch.com/tools/ipo-calendar"):
    resp = requests.get(marketwatch_url)
    html = resp.text
    print(html)
    try:
        html_table_list = pd.read_html(html, attrs={"class": "ranking"})
        lastweek, upcoming = html_table_list[1], html_table_list[2]

        column_names = ['Company Name', 'Proposed Symbol', 'Exchange', 'Price Range', 'Shares',
       'Week Of']
        upcoming.columns = column_names
        print(upcoming)
        for index, row in upcoming.iterrows():
            listing = row
            print(row)
            name = listing["Company Name"]
            symbol = listing["Proposed Symbol"]
            ex = listing["Exchange"]
            priceRange = listing["Price Range"]
            shares = listing["Shares"]
            week = listing["Week Of"]
            date = convert_ipo_date(week)

            output_str = f"""{name}/{symbol}/{ex} \n - {priceRange} \n - Shares: {shares}
            """
            make_event_in_gcal(output_str, date)
            try:
                firstItem = searchGoogle(f"{symbol} {ex}")
                content, embeds = mapItemForDiscord(firstItem)
                send_message(content, embeds)
            except Exception as e:
                print(e)
                pass
            # send data to discord
        # send data to calendar
        return lastweek, upcoming
    except Exception as e:
        ic("Error message here")
        ic(e)
        raise Exception(e)
        return None, None



