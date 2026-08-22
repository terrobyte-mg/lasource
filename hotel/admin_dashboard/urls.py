# admin_dashboard/urls.py
from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Authentification
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Dashboard et pages protégées
    path('', views.admin_dashboard, name='dashboard'),
    path('reservations/', views.admin_reservations, name='reservations'),
    path('chambres/', views.admin_chambres, name='chambres'),

    # Actions sur les réservations
    path('reservation/<int:reservation_id>/confirmer/', views.confirmer_reservation, name='confirmer_reservation'),
    path('reservation/<int:reservation_id>/annuler/', views.annuler_reservation, name='annuler_reservation'),
    path('reservation/<int:reservation_id>/', views.carte_reservation, name='carte_reservation'),

    # Actions sur les chambres
    path('chambre/<int:chambre_id>/toggle/', views.toggle_disponibilite_chambre, name='toggle_disponibilite'),
    path('chambre/ajouter/', views.ajouter_chambre, name='ajouter_chambre'),

    path('chambres/modifier/<int:chambre_id>/', views.modifier_chambre, name='modifier_chambre'),
    path('chambres/image/supprimer/<int:image_id>/', views.supprimer_image_chambre, name='supprimer_image'),

    path('chambre/<int:chambre_id>/supprimer/', views.supprimer_chambre, name='supprimer_chambre'),

    # Actions sur l'accueil
    path('images-accueil/', views.images_accueil, name='images_accueil'),
    path('images-accueil-ajouter/', views.ajouter_image_accueil, name='images_accueil_ajouter'),
    path('images-accueil/<int:image_id>/toggle/', views.toggle_image_actif, name='images_accueil_toggle'),
    path('images-accueil/<int:image_id>/supprimer/', views.supprimer_image, name='images_accueil_supprimer'),

]