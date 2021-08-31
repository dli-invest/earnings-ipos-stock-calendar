import os
import requests
from es_cal.discord import send_message
BASE_SEARCH_URL="https://www.googleapis.com/customsearch/v1?"


"""
    1. First, we get the search data from the Google Custom Search API.
    2. Then, we parse the response to get the first item from the search results.
    3. Then, we map the item to a dictionary that we can send to Discord.
    4. Finally, we send the message to Discord.
"""

def searchGoogle(query: str):
    gsk = os.getenv("GOOGLE_SEARCH_KEY")
    gsecx = os.getenv("GOOGLE_SEARCH_ENGINE_CX")
    search_url = f"{BASE_SEARCH_URL}q={query}&key={gsk}&cx={gsecx}"
    r = requests.get(search_url)
    data = r.json()
    return parseResponse(data)


def parseResponse(searchData: dict):
    item = searchData.get('items', [None])[0]
    if item == None:
        raise Exception ('No search data returned')
    return item

def mapItemForDiscord(item: dict):
    content = item.get('title')
    embed = {
        'title': item.get('title'),
        'description': item.get('snippet'),
        'url': item.get('link'),
    }
    embeds = [embed]
    return content, embeds