"""SmartDevice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from sensors import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('rooms/', views.room_list),
    path('room/<int:pk>', views.room_detail),
    path('device_scan/<str:device_id>', views.device_scan),
    path('register_user/', views.register_user),
    path('camera_record/', views.face_record),
    path('sensor_stream/<str:device_id>', views.sensor_data_stream),
    path('fetch_by/', views.fetch_sensor_data_by),
    path('sec_sensor_data/', views.sec_sensor_data),
    path('get_sensor_data/', views.get_sensor_data),
    path('get_location_data/', views.fetch_location_data_by),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # query apis
    path('room/', views.room),
    path('room_info/', views.room_info),
    path('people_building/', views.people_building),
    path('people_room/', views.people_room),
    path('person_room/', views.person_room),
    path('utilization/', views.utilization)
]
