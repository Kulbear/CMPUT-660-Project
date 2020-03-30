from sensors.models import Room, Device, DeviceData
import requests
import json
from pprint import pprint

token = '7b8e7f8b-63cc-465c-9dad-b488b2351096'

d = {
    "Room_1_1_112": {
        "PCL1_11112_OC_1_TL": {
            "UUID": "6200d218-1f09-42ac-9df2-968c7d2fced1",
            "Type": "Room_Outlet_Controller"
        },
        "PCL1_11112_MS_1_TL": {
            "UUID": "82b93bb1-53ca-4298-b823-5f1b2a660b2d",
            "Type": "Room_Motion_Sensor"
        },
        "PCL1_11112_TS_1_TL": {
            "UUID": "3ac58526-fba8-4adf-9788-70fafef3a146",
            "Type": "Room_Button"
        },
        "PCL1_11112_LC_1_TL": {
            "UUID": "709459f7-dd70-43b7-b4d7-c4a4b4ab885a",
            "Type": "Room_Lock_Controller"
        }
    }
}

for key in d:
    # create room
    room = Room(room_id=key, name=key, room_description='')
    room.save()

print('Initialized Rooms')

for r_id in d:
    room = Room.objects.get(room_id=r_id)
    device_ids = d[r_id]
    for device_info in device_ids:
        device_id = device_ids[device_info]['UUID']
        tp = device_ids[device_info]['Type']
        print(device_id)
        print(tp)
        device = Device(
            device_id=device_id, room=room, device_type=tp,
            device_name=device_id, device_label=device_id, device_description=device_id,
            location_id=key, complete_setup=True, hub_id='temp', network_type='ZIGBEE',
            network_sec='temp')
        device.save()

print('Initialized Devices')

for r_id in d:
    device_ids = d[r_id]
    for device_info in device_ids:
        device_id = device_ids[device_info]['UUID']
        tp = device_ids[device_info]['Type']
        device = Device.objects.get(device_id=device_id)

        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {token}"}
        a = requests.get(f"https://api.smartthings.com/v1/devices/{device_id}/status", headers=headers)
        result = json.loads(a.content.decode('utf-8'))
        data = result['components']['main']
        pprint(data)

        # common properties
        actuator = str(data.get('actuator', {}))
        configuration = str(data.get('configuration', {}))
        # health_check = str(data.get('healthCheck', {}))
        health_check = ''
        refresh = str(data.get('refresh', {}))
        sensor = str(data.get('sensor', {}))

        # outlet only
        outlet_switch_value = str(None)
        if 'outlet' in data:
            outlet_switch_value = data['outlet']['switch']['value']

        power_unit = str(None)
        power_value = 0.
        if 'powerMeter' in data:
            power_unit = data['powerMeter']['power']['unit']
            power_value = float(data['powerMeter']['power']['value'])

        # motion sensor
        motion_sensor_value = str(None)
        temperature_unit = str(None)
        temperature_value = -999.
        if 'motionSensor' in data:
            motion_sensor_value = data['motionSensor']['motion']['value']
            temperature_unit = data['temperatureMeasurement']['temperature']['unit']
            temperature_value = float(data['temperatureMeasurement']['temperature']['value'])

        lock_data = str(None)
        lock_value = str(None)
        if 'lock' in data:
            lock_data = data['lock']['lock']['data']
            lock_value = data['lock']['lock']['value']

        battery_value = -1.
        if 'battery' in data:
            battery_value = float(data['battery']['battery']['value'])

        holdable_button = str(None)
        if 'button' in data:
            holdable_button = data['button']['button']['value']

        print('act', actuator)
        print('configuration', configuration)
        print('health_check', health_check)
        print('outlet_switch_value', outlet_switch_value)
        print('motion_sensor_value', motion_sensor_value)
        print('temperature_unit', temperature_unit)
        print('temperature_value', temperature_value)
        print('lock_data', lock_data)
        print('lock_value', lock_value)
        print('battery_value', battery_value)
        print('\n\n')

        device_data = DeviceData(
            device=device,
            actuator=actuator,
            configuration=configuration,
            health_check=health_check,
            refresh=refresh,
            sensor=sensor,
            battery_value=battery_value,
            lock_data=lock_data, lock_value=lock_value,
            motion_sensor_value=motion_sensor_value,
            temperature_unit=temperature_unit,
            temperature_value=temperature_value,
            power_unit=power_unit, power_value=power_value,
            holdable_button=holdable_button,
            outlet_switch_value=outlet_switch_value
        )
        device_data.save()

#     device_id = models.ForeignKey(Device, on_delete=models.CASCADE)
#     actuator = models.CharField(max_length=100)
#     configuration = models.CharField(max_length=255)
#     health_check = models.TextField()
#     refresh = models.CharField(max_length=40)
#     sensor = models.CharField(max_length=40)

#     battery_value = models.FloatField()
#     lock_data = models.CharField(max_length=40)
#     lock_value = models.CharField(max_length=40)
#     motion_sensor_value = models.CharField(max_length=10)
#     temperature_unit = models.CharField(max_length=1, choices=TEMP_UNITS)
#     temperature_value = models.FloatField()
#     power_unit = models.CharField(max_length=1, choices=POWER_UNITS)
#     power_value = models.FloatField()
#     holdable_button = models.CharField(max_length=10)
#     outlet_switch_value = models.CharField(max_length=10)
#     modified_by = models.DateTimeField()
#     create_by = models.DateTimeField()
