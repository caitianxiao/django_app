from django.urls import path
from game.views import play

urlpatterns = [
    path('', play, name = "play game"),
]
