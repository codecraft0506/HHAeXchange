import os
import requests
from dotenv import load_dotenv
load_dotenv()

DC_URL = os.environ.get('DC_URL')

def send_notification(message, user='', image_path=None):
    payload = {
        'content': f"{user} {message}",
    }
    files = {'file': open(image_path, 'rb')} if image_path else None
    requests.post(DC_URL, data=payload, files=files)

if __name__ == '__main__':
    send_notification('DC Notify Test', 'Ryan', 'test_img.jpg')
