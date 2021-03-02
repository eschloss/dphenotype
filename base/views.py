from django.http import HttpResponse


def home(request):
    response = ""
    response += "Hello World<br/>"

    return HttpResponse(response)
