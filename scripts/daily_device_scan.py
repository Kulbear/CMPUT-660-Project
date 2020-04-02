# Crontab run this script everyday at 12:00 am
import requests
import json

API_ENDPOINT = 'http://127.0.0.1:8000/device_scan/'
API_HOST_1 = 'https://api.smartthings.com'
API_HOST_2 = 'http://pacific-temple-42851.herokuapp.com'
token = '7b8e7f8b-63cc-465c-9dad-b488b2351096'
headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"}

for host in [API_HOST_1, API_HOST_2]:
    req = requests.get(host + '/v1/devices/', headers=headers)
    result = json.loads(req.content.decode('utf-8'))
    data = result['items']
    for item in data:
        r = requests.post(url=API_ENDPOINT + item['deviceId'], json=item)
        print(r, item['deviceId'])
