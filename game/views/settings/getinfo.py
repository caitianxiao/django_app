from django.http import JsonResponse
from game.models.player.player import Player

def getinfo_web(request):
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({
            'result' : "login fault",
        })
    else:
        player = Player.objects.all()[0]
        return JsonResponse({
            'result' : "success",
            'username' : player.user.username,
            'photo' : player.photo,
        })




def getinfo_xxx(requset):
    pass


def getinfo(request):
    platform = request.GET.get('platform')
    if platform == "WEB":
        return getinfo_web(request)
