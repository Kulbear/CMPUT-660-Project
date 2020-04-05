from django.contrib.auth.models import User, Group
from sensors.models import Room, Device, DeviceData, LocationData, CameraRecord, SensorData
from rest_framework import serializers


class LocationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationData
        fields = ['location', 'name', 'created_by']

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['location', 'sensor_data', 'created_by']


class CameraRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraRecord
        fields = ['person_id', 'camera_id', 'person_name']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ['room_id', 'name', 'room_description']


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'device_id', 'room', 'device_type',
            'device_name', 'device_label', 'device_description',
            'location_id', 'complete_setup', 'hub_id',
            'network_type', 'network_sec'
        ]


class DeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = [
            'device', 'actuator', 'configuration', 'health_check',
            'refresh', 'sensor', 'battery_value', 'lock_data',
            'lock_value', 'motion_sensor_value', 'temperature_unit',
            'temperature_value', 'power_unit', 'power_value',
            'holdable_button', 'outlet_switch_value'
        ]


class PersonSeiralizer(serializers.ModelSerializer):
    class Meta:
        model = DeviceData
        fields = [
            'person_id', 'face_embedding',
            'name', 'identity', 'email'
        ]
