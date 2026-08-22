from django.urls import path
from . import views

app_name = 'chambres'

urlpatterns = [
    path('', views.liste_chambres, name='liste'),
]