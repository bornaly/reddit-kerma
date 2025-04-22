import sys
import os
import requests
import datetime

# Dynamically add root directory to sys.path so config can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config import Botconfig  # Now this works without red underline

def write_log(data: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {data}"

    if Botconfig.discord_webhook is True and Botconfig.webhook:
        try:
            url = Botconfig.webhook
            payload = {
                "embeds": [
                    {
                        "title": "📘 Reddit Bot Log",
                        "description": formatted_message,
                        "color": 16711680
                    }
                ]
            }

            response = requests.post(url, json=payload)
            if response.status_code != 204:
                print(f"[WEBHOOK] Error: {response.status_code} - {response.text}")
            else:
                print("[WEBHOOK] Sent successfully")

        except Exception as e:
            print(f"[WEBHOOK ERROR] - {e}")
    else:
        try:
            with open("log.txt", "a", encoding="utf-8") as log:
                log.write(formatted_message + "\n")
                log.write("---------------------------\n")
        except Exception as e:
            print(f"[FILE LOGGING ERROR] - {e}")
