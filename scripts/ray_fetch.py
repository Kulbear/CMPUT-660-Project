import requests
import json
import ray

ray.init()

API_ENDPOINT = 'http://0.0.0.0:8000/sensor_stream/'
API_HOST_1 = 'https://api.smartthings.com'
API_HOST_2 = 'http://pacific-temple-42851.herokuapp.com'
token = '7b8e7f8b-63cc-465c-9dad-b488b2351096'
headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"}

target = []
device_ids = [[], []]
for idx, host in enumerate([API_HOST_1, API_HOST_2]):
    req = requests.get(host + '/v1/devices/', headers=headers)
    result = json.loads(req.content.decode('utf-8'))
    for item in result['items']:
        device_ids[idx].append(item['deviceId'])

target = []
target_ids = []
for g_idx, group in enumerate(device_ids):
    for d_id in group:
        a = requests.get(f"{API_HOST_1 if g_idx == 0 else API_HOST_2}/v1/devices/{d_id}/status", headers=headers)
        target.append(f"{API_HOST_1 if g_idx == 0 else API_HOST_2}/v1/devices/{d_id}/status")
        target_ids.append(d_id)
        try:
            result = json.loads(a.content.decode('utf-8'))
            data = result['components']['main']
            r = requests.post(url=API_ENDPOINT + d_id, json=data)
        except:
            print(d_id, 'failed!')


@ray.remote
def get_sensor_data(target, target_id):
    a = requests.get(target, headers=headers)
    try:
        result = json.loads(a.content.decode('utf-8'))
        data = result['components']['main']
        requests.post(url=API_ENDPOINT + target_id, json=data)
    except:
        print(d_id, 'failed!')

import time
while True:
    time.sleep(5)
    print('Done 1 cycle')
    futures = [get_sensor_data.remote(target[idx], target_ids[idx]) for idx in range(len(target))]


