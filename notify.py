import os
import requests
from dotenv import load_dotenv
load_dotenv()

DC_URL = os.environ.get('DC_URL')

def send_notification(message, user=''):
    payload = {
        'content': f"{user} {message}",
    }
    requests.post(DC_URL, json=payload)

if __name__ == '__main__':
    send_notification('DC Notify Test', 'Ryan')
