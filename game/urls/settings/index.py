from django.urls import path
from game.views.settings.getinfo import getinfo
from game.views.settings.login import signin
from game.views.settings.register import register
from game.views.settings.logout import signout
urlpatterns = [
    path("getinfo/", getinfo, name = "settings_getinfo"),
    path("login/", signin, name = "login_remote"),
    path("register/", register, name = "register_remote"),
    path("logout/", signout, name = "logout_remote")
]
