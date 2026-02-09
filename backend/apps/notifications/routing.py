"""
WebSocket URL routing for notifications app.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Real-time notifications
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),

    # Real-time chat with AI agent
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<conversation_id>[0-9a-f-]+)/$', consumers.ChatConsumer.as_asgi()),
]
