# Create your models here.
from django.db import models

DEVICE_TYPES = [
    ('Outlet', 'Room_Outlet_Controller'),
    ('Camera', 'Room_Camera'),
    ('Lock', 'Room_Lock_Controller'),
    ('Motion', 'Room_Motion_Sensor'),
    ('Temperature', 'Room_Temperature_Sensor')
]

NETWORK_TYPES = [
    ('ZIGBEE', 'ZIGBEE'),
    ('ZWAVE', 'ZWAVE')
]

TEMP_UNITS = [
    ('F', 'Fahrenheit'),
    ('C', 'Celsius')
]

POWER_UNITS = [
    ('W', 'Watts')
]


class Room(models.Model):
    room_id = models.CharField(max_length=40, primary_key=True)
    name = models.CharField(max_length=100)
    room_description = models.TextField()
    create_by = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.room_id}'


class Device(models.Model):
    device_id = models.CharField(max_length=40, primary_key=True)
    room = models.CharField(max_length=40)
    device_type = models.CharField(max_length=40, choices=DEVICE_TYPES)
    device_name = models.CharField(max_length=40)
    device_label = models.CharField(max_length=40)
    device_description = models.TextField()
    location_id = models.CharField(max_length=40)
    complete_setup = models.BooleanField()
    hub_id = models.CharField(max_length=40)
    network_type = models.CharField(max_length=40, choices=NETWORK_TYPES)
    network_sec = models.CharField(max_length=40)


class DeviceData(models.Model):
    device = models.CharField(max_length=40)
    actuator = models.CharField(max_length=100)
    configuration = models.CharField(max_length=255)
    health_check = models.TextField()
    refresh = models.CharField(max_length=40)
    sensor = models.CharField(max_length=40)
    face_name = models.CharField(max_length=40)
    face_email = models.CharField(max_length=100)
    battery_value = models.FloatField()
    lock_data = models.CharField(max_length=40)
    lock_value = models.CharField(max_length=40)
    motion_sensor_value = models.CharField(max_length=10)
    temperature_unit = models.CharField(max_length=10, choices=TEMP_UNITS)
    temperature_value = models.FloatField()
    power_unit = models.CharField(max_length=10, choices=POWER_UNITS)
    power_value = models.FloatField()
    holdable_button = models.CharField(max_length=10)
    outlet_switch_value = models.CharField(max_length=10)
    create_by = models.DateTimeField(auto_now_add=True)


class Person(models.Model):
    person_id = models.CharField(max_length=40, primary_key=True)
    face_embedding = models.TextField()
    name = models.CharField(max_length=100)
    identity = models.CharField(max_length=100)
    email = models.EmailField()


class CameraRecord(models.Model):
    person_id = models.CharField(max_length=40)
    person_name = models.CharField(max_length=40)
    record_time = models.DateTimeField(auto_now_add=True)
    camera_id = models.TextField()


class SensorData(models.Model):
    location = models.TextField()
    sensor_data = models.TextField()
    created_by = models.DateTimeField(auto_now_add=True)


class LocationData(models.Model):
    name = models.CharField(max_length=40)
    location = models.CharField(max_length=40)
    created_by = models.DateTimeField(auto_now_add=True)
