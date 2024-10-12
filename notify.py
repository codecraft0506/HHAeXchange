import os
import requests
from dotenv import load_dotenv
load_dotenv()

line_token = os.getenv('LINE_TOKEN')

def send_line_notification(message, user=''):
    headers = {
        'Authorization': f'Bearer {line_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        'message': f"{user} {message}",
    }
    requests.post('https://notify-api.line.me/api/notify', headers=headers, data=payload)