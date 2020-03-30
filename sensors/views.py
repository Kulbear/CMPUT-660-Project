from django.contrib.auth.models import User, Group
from sensors.models import Room, Device, DeviceData, Person
from rest_framework import viewsets
from rest_framework import permissions
from sensors.serializers import UserSerializer, GroupSerializer, RoomSerializer
from sensors.serializers import DeviceSerializer, DeviceDataSerializer, PersonSeiralizer
from pprint import pprint
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def sensor_data_stream(request, format=None):
    data = request.data
    device_id = data['device_id']
    data = data['components']['main']
    pprint(data)

    # find device
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

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


@api_view(['GET', 'POST'])
def room_list(request, format=None):
    if request.method == 'GET':
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = Room(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'POST', 'DELETE'])
def room_detail(request, pk, format=None):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    elif request.method in ['PUT', 'POST']:
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows rooms to be viewed or edited.
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
