from django.urls import path
from . import views

app_name = 'reservations'   # namespace

urlpatterns = [
    path('', views.reserver, name='reserver'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('api/disponibilite/', views.disponibilite_api, name='disponibilite_api'),
    path('api/dates-bloquees/', views.dates_bloquees_api, name='dates_bloquees_api'),
]