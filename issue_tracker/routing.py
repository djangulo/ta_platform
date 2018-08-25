from django.urls import path
from channels.routing import ProtocolTypeRouter

from issue_tracker import consumers

websocket_urlpatterns = [
    path('ws/its/<str:room_name>/', consumers.ChatConsumer),
]
