from django.shortcuts import render

# Create your views here.


def dictionary(request):
    return render(request, 'features/dictionary.html', None)
