from django.urls import path

from . import views


urlpatterns = [
    path('dictionary/', views.dictionary, name='dictionary'),
]