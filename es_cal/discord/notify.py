import requests
import os
import json


def send_message(content, embeds=[]):
    try:
        payload = {"content": content, "embeds": embeds}
        DISCORD_WEBHOOK = os.environ.get("NOTIFICATION_DISCORD_WEBHOOK")
        if DISCORD_WEBHOOK is None:
            print("FAILED TO SEND DISCORD MESSAGE")
            return
        r = requests.post(
            DISCORD_WEBHOOK,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        return r.json()
    except Exception as e:
        print(e)
