import requests
import json

API_ENDPOINT = 'http://127.0.0.1:8000/sensor_stream/'
API_HOST_1 = 'https://api.smartthings.com'
API_HOST_2 = 'http://pacific-temple-42851.herokuapp.com'
token = '7b8e7f8b-63cc-465c-9dad-b488b2351096'
headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"}

device_ids = [[], []]
for idx, host in enumerate([API_HOST_1, API_HOST_2]):
    req = requests.get(host + '/v1/devices/', headers=headers)
    result = json.loads(req.content.decode('utf-8'))
    for item in result['items']:
        device_ids[idx].append(item['deviceId'])

print(device_ids)
len(device_ids[0]), len(device_ids[1])

while True:
    for g_idx, group in enumerate(device_ids):
        for d_id in group:
            print(d_id)
            a = requests.get(f"{API_HOST_1 if g_idx == 0 else API_HOST_2}/v1/devices/{d_id}/status", headers=headers)
            try:
                result = json.loads(a.content.decode('utf-8'))
                data = result['components']['main']
                r = requests.post(url=API_ENDPOINT + item['deviceId'], json=item)
                print(d_id, r)
            except:
                print(d_id, 'failed!')
