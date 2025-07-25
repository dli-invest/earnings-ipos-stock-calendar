import requests
from bs4 import BeautifulSoup
import pandas as pd
from icecream import ic
import datetime
from es_cal.gcal import make_event_in_gcal
from es_cal.discord import send_message
from es_cal.browser.googleSearch import searchGoogle, mapItemForDiscord

import requests
import os
import random

def get_and_set_selenium_proxy():
    """
    Scrapes a list of SOCKS5 proxies from a public URL, selects the first one,
    and prints a GitHub Actions command to set an environment variable
    'SELENIUM_PROXY' with the chosen proxy.

    This function is designed to be run within a GitHub Actions workflow.
    The output will be captured by GitHub Actions and used to set the
    environment variable for subsequent steps.
    """
    proxy_list_url = "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt"
    proxy_env_var_name = "SELENIUM_PROXY"

    print(f"Attempting to fetch proxies from: {proxy_list_url}")

    try:
        response = requests.get(proxy_list_url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        proxies = [line.strip() for line in response.text.splitlines() if line.strip()]

        if not proxies:
            print("No proxies found in the list. Cannot set SELENIUM_PROXY.")
            return

        # For simplicity, we'll use the first proxy found.
        # In a real-world scenario, you might want to implement proxy testing
        # to ensure it's functional before using it.
        selected_proxy_ip_port = random.choice(proxies)
        proxy_string = selected_proxy_ip_port

        # GitHub Actions special command to set an environment variable for subsequent steps
        # This will write "SELENIUM_PROXY=socks5://IP_ADDRESS:PORT" to the GITHUB_ENV file
        # which GitHub Actions automatically reads.
        return proxy_string

    except requests.exceptions.RequestException as e:
        print(f"Error fetching proxies: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def convert_ipo_date(date: str):
    return datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')

def fetch_ipos(marketwatch_url = "https://www.marketwatch.com/tools/ipo-calendar"):
    socks5_proxy = get_and_set_selenium_proxy()
    resp = requests.get(marketwatch_url, proxies=dict(http=socks5_proxy,
                                 https=socks5_proxy))
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



