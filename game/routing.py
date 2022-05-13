from django.urls import path
from game.consumers.multiplayer.index import MultiPlayer


websocket_urlpatterns = [
        path("ws/multiplayer/", MultiPlayer.as_asgi(), name=""),
]
