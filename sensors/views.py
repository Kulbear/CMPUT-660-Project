from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from sensors.models import Room, Device, DeviceData, Person, CameraRecord, SensorData
import face_recognition
import datetime
from django.db.models.functions import Now
from rest_framework import viewsets
from rest_framework import permissions
from sensors.serializers import UserSerializer, GroupSerializer, RoomSerializer, CameraRecordSerializer
from sensors.serializers import DeviceSerializer, DeviceDataSerializer, PersonSeiralizer, SensorDataSerializer
from pprint import pprint
import ast
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def sec_sensor_data(request):
    req_data = request.data

    s = SensorData(location=req_data['location'], sensor_data=req_data['sensor_data'],
                   created_by=Now())
    s.save()
    return Response(status=status.HTTP_201_CREATED)
    # except:
    #     return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_sensor_data(request):
    now = datetime.datetime.now()
    now_plus_10 = now + datetime.timedelta(minutes=1)
    data = SensorData.objects.filter(created_by__range=(now - datetime.timedelta(minutes=10), now_plus_10)).order_by(
        '-created_by').values()
    print(data)
    try:
        sensor_data_1 = data[0]['sensor_data']
        location = data[0]['location']
        sensor_data_2 = data[1]['sensor_data']
        return Response(data={'current_sensor_data': sensor_data_1, 'prev_sensor_data': sensor_data_2,
                              'location': location}, status=status.HTTP_202_ACCEPTED)
    except:
        return Response(data={}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def fetch_sensor_data_by(request):
    req_data = request.data
    start = req_data.get('start', None)
    end = req_data.get('end', None)
    device_type = req_data.get('device_type', None)
    device_id = req_data.get('device_id', None)

    d_data = None
    if start and end:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        d_data = DeviceData.objects.filter(create_by__range=(start_date, end_date))
    if device_id:
        if d_data:
            d_data = d_data.filter(device=device_id)
        else:
            d_data = DeviceData.objects.filter(device=device_id)

    if d_data == None:
        d_data = DeviceData.objects.all()

    d_data = d_data.values()
    return Response({'data': d_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register_user(request, format=None):
    req_data = request.data
    face_encodings = req_data['face_encodings']
    name = req_data['name']
    email = req_data['email']
    identity = req_data['identity']
    try:
        try:
            person = Person.objects.get(email=email)
            person.name = name
            person.identity = identity
            face_embedding = ast.literal_eval(person.face_embedding)
            face_embedding.extend(face_encodings)
            person.face_embedding = face_embedding
            person.save()
            return Response(status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            person = Person(name=name, email=email, identity=identity, face_embedding=str(face_encodings))
            person.save()
            return Response(status=status.HTTP_202_ACCEPTED)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def face_record(request, format=None):
    req_data = request.data
    face_encodings = req_data['face_encodings']
    camera_id = req_data['camera_id']

    database_face_encodings = []
    database_face_names = []
    database_face_ids = []
    people = Person.objects.all().values()
    for person in people:
        database_face_ids.append(person['person_id'])
        database_face_encodings.append(person['face_embedding'])
        database_face_names.append(person['name'])

    detected_people = []
    # start to compare with database
    for encoding in face_encodings:
        matches = face_recognition.compare_faces(database_face_encodings,
                                                 encoding)
        print(matches)
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}
            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = database_face_names[i]
                counts[name] = counts.get(name, 0) + 1
            # determine the recognized face with the largest number of
            # votes (note: in the event of an unlikely tie Python will
            # select first entry in the dictionary)
            name = max(counts, key=counts.get)
            p_idx = database_face_names.index(name)

            cam_record = CameraRecord(person_id=database_face_ids[p_idx], person_name=name,
                                      camera_id=camera_id)
            if cam_record.is_valid():
                cam_record.save()
    return Response({}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def device_scan(request, device_id):
    item = request.data
    print(device_id)
    # print(item)
    try:
        if item['type'] == 'HUB':
            device = Device(device_id=device_id, device_name=item['name'],
                            device_label=item['label'], location_id='',
                            device_type='SmartThings v3 Hub', room='', complete_setup=True,
                            hub_id=item['deviceId'], network_type='', network_sec='',
                            device_description='')
        else:
            device = Device(device_id=device_id, device_name=item['name'],
                            device_label=item['label'], location_id=item['locationId'],
                            device_type=item['dth']['deviceTypeName'], room=item['roomId'],
                            complete_setup=item['dth']['completedSetup'],
                            hub_id=item['dth']['hubId'],
                            network_type=item['dth']['deviceNetworkType'],
                            network_sec=item['dth']['networkSecurityLevel'],
                            device_description=item['dth']['deviceTypeName'])
    except Exception as e:
        print('Error', e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        device.save()
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def sensor_data_stream(request, device_id=None):
    data = request.data

    # common properties
    actuator = str(data.get('actuator', {}))
    configuration = str(data.get('configuration', {}))
    # health_check = str(data.get('healthCheck', {}))
    health_check = ''
    refresh = str(data.get('refresh', {}))
    sensor = str(data.get('sensor', {}))

    face_name = ''
    face_email = ''
    if 'face' in data:
        face_name = data['face']['name']
        face_email = data['face']['email']

    # outlet only
    outlet_switch_value = ''
    if 'outlet' in data:
        outlet_switch_value = data['outlet']['switch']['value']

    power_unit = ''
    power_value = 0.
    if 'powerMeter' in data:
        power_unit = data['powerMeter']['power']['unit']
        power_value = float(data['powerMeter']['power']['value'])

    # motion sensor
    motion_sensor_value = ''
    temperature_unit = ''
    temperature_value = -999.
    if 'motionSensor' in data:
        motion_sensor_value = data['motionSensor']['motion']['value']
        temperature_unit = data['temperatureMeasurement']['temperature']['unit']
        temperature_value = float(data['temperatureMeasurement']['temperature']['value'])

    lock_data = ''
    lock_value = ''
    if 'lock' in data:
        lock_data = data['lock']['lock']['data']
        lock_value = data['lock']['lock']['value']

    battery_value = -1.
    if 'battery' in data:
        battery_value = float(data['battery']['battery']['value'])

    holdable_button = ''
    if 'button' in data:
        holdable_button = data['button']['button']['value']
    try:
        device_data = DeviceData(
            device=device_id,
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
            outlet_switch_value=outlet_switch_value,
            face_name=face_name,
            face_email=face_email,
            create_by=Now()
        )

        device_data.save()
        return Response(status=status.HTTP_201_CREATED)

    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
