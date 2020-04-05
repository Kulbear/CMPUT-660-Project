import requests
import json
from pprint import pprint
from collections import defaultdict
import datetime


def update_person_location(sensor_data, all_previous_location):
    sensor_data['time'] = datetime.datetime.now()
    if sensor_data["time"].second + sensor_data["time"].minute + sensor_data["time"].hour == 0:
        return dict()

    doors = accessible_zone_sensor_map["home"]

    # Deal with new incoming person
    # Get all gates
    for door in doors:
        # Get camera for each gate
        for sensor in sensor_data["data"][door].values():
            if sensor["type"] == "Room_Door_Camera":
                # Check existence of the person
                for name in sensor["value"]:
                    if name not in all_previous_location:
                        all_previous_location[name] = "home"

    # Update the location
    for name in all_previous_location:
        # Get previous location
        if name == 'time':
            continue
        previous_location = all_previous_location[name]
        next_person = False
        # Get all possible door sensor data
        for room in accessible_zone_sensor_map[previous_location]:
            for sensor in sensor_data["data"][room].values():
                if sensor["type"] == "Room_Door_Camera":
                    # Check if the person trying to open this door
                    if name in sensor["value"]:
                        if room == previous_location:
                            all_previous_location[name] = door_connect_zone[room]
                        else:
                            all_previous_location[name] = room
                        next_person = True
                if next_person:
                    break
            if next_person:
                break

    all_previous_location["time"] = sensor_data["time"]

    return all_previous_location


accessible_zone_sensor_map = {
    "home": ("Room_1_1_184",),
    "Room_1_1_184": ("Room_1_1_150", "Room_1_1_184"),
    "Room_1_1_150": ("Room_1_1_140", "Room_1_1_141", "Room_1_1_142", "Room_1_1_143", "Room_1_1_144", "Room_1_1_150"),
    "Room_1_1_140": ("Room_1_1_140",),
    "Room_1_1_141": ("Room_1_1_141",),
    "Room_1_1_142": ("Room_1_1_142",),
    "Room_1_1_143": ("Room_1_1_143",),
    "Room_1_1_144": ("Room_1_1_144",)
}

door_connect_zone = {
    "Room_1_1_184": "home",
    "Room_1_1_150": "Room_1_1_184",
    "Room_1_1_140": "Room_1_1_150",
    "Room_1_1_141": "Room_1_1_150",
    "Room_1_1_142": "Room_1_1_150",
    "Room_1_1_143": "Room_1_1_150",
    "Room_1_1_144": "Room_1_1_150"
}

name_type_template = {
    'Room_Outlet_Controller': 'PCL1_{}_OC_1_TL',
    'Room_Motion_Sensor': 'PCL1_{}_MS_1_TL',
    'Room_Temperature_Sensor': 'PCL1_{}_TS_1_TL',
    'Room_Lock_Controller': 'PCL1_{}_LC_1_TL',
    'Room_Door_Camera': 'PCL1_{}_DC_1_TL'
}

API_ENDPOINT = 'http://127.0.0.1:8000/'
API_HOST_1 = 'https://api.smartthings.com'
API_HOST_2 = 'http://pacific-temple-42851.herokuapp.com'
token = '7b8e7f8b-63cc-465c-9dad-b488b2351096'
headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"}

req = requests.get(API_HOST_2 + '/v1/locations', headers=headers)
first_location = json.loads(req.content.decode('utf-8'))

room_device_mapping = defaultdict(list)
for host in [API_HOST_2]:
    req = requests.get(host + '/v1/devices/', headers=headers)
    result = json.loads(req.content.decode('utf-8'))
    data = result['items']
    for data_item in data:
        try:
            assert len(data_item['roomId']) < 16
            room_device_mapping[data_item['roomId']].append((data_item['deviceId'], data_item['deviceTypeName']))
        except:
            room_device_mapping['Room_1_1_140'].append(
                (data_item['deviceId'], data_item.get('deviceTypeName', 'SmartThings Hub')))

import time

while True:
    try:
        time.sleep(2)
        req = requests.get(API_HOST_2 + '/v1/devices/all', headers=headers)
        all_device_data = json.loads(req.content.decode('utf-8'))

        sensor_data = {}
        sensor_data['data'] = defaultdict(dict)
        for room in room_device_mapping:
            for d_id, d_type in room_device_mapping[room]:
                try:
                    result = all_device_data['data'][d_id]
                    data = result['components']['main']
                    if 'outlet' in data:
                        device_type = 'Room_Outlet_Controller'
                        value = data['powerMeter']['power']['value']
                    elif 'motionSensor' in data:
                        device_type = 'Room_Motion_Sensor'
                        value = data['motionSensor']['motion']['value']
                    elif 'temperatureMeasurement' in data:
                        device_type = 'Room_Temperature_Sensor'
                        value = data['temperatureMeasurement']['temperature']['value']
                    elif 'lock' in data:
                        device_type = 'Room_Lock_Controller'
                        value = data['lock']['lock']['value']
                    elif 'face' in data:
                        device_type = 'Room_Door_Camera'
                        value = data['face']['face']['name']
                    sensor_data['data'][room][name_type_template[device_type].format(''.join(room.split('_')[-3:]))] = {
                        'type': device_type,
                        'value': value
                    }
                except:
                    print(d_id, 'failed!')

        sensor_data['data'] = dict(sensor_data['data'])
        first_location = update_person_location(sensor_data, first_location)
        print(first_location)
        del sensor_data['time']
        location_data = dict(first_location)
        del location_data['time']
        upload_data = {'sensor_data': str(sensor_data), 'location': str(location_data)}
        r = requests.post(url=API_ENDPOINT + 'sec_sensor_data/', json=upload_data)
    except:
        pass