from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def imageEditor_view(request, *args, **kwargs):
    context = {

    }
    return render(request, "imageEditor.html", context)
