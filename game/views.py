from django.http import HttpResponse

# Create your views here.
def play(request):
    s1 = '<h1 style="color:red;margin:auto;background-color:blue">This is my game!!!</h1>'
    return HttpResponse(s1)
