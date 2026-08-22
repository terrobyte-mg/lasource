# admin/views.py
from datetime import datetime, date
from datetime import timedelta
from decimal import Decimal
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from admin_dashboard.forms import ChambreForm, ImageAccueilForm
from chambres.models import Chambre, ChambreImage, ImageAccueil
from reservations.models import Reservation


def envoyer_email_confirmation_reservation(reservation):
    """Envoyer un e-mail de confirmation de réservation au client"""
    try:
        # Calcul des détails
        nb_jours = (reservation.date_depart - reservation.date_arrivee).days
        prix_total = nb_jours * reservation.chambre.prix

        # Sujet
        sujet = f"✅ Réservation confirmée - Hôtel La Source"

        # Message texte brut
        message_texte = f"""
Bonjour {reservation.prenom} {reservation.nom},

Nous avons le plaisir de vous confirmer votre réservation à l'Hôtel La Source.

📋 DÉTAILS DE VOTRE RÉSERVATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Numéro de réservation : #{reservation.id}
Chambre : {reservation.chambre.numero}
Type : {reservation.chambre.get_type_display()}

📅 DATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Arrivée : {reservation.date_arrivee.strftime('%d/%m/%Y')}
Départ : {reservation.date_depart.strftime('%d/%m/%Y')}
Durée : {nb_jours} nuit{"s" if nb_jours > 1 else ""}

💰 TARIF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prix total : {prix_total:,.0f} Ar

📍 ADRESSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hôtel La Source
[Votre adresse complète]

📞 CONTACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Téléphone : [Votre numéro]
Email : {settings.DEFAULT_FROM_EMAIL}

Nous vous attendons avec impatience !

Cordialement,
L'équipe de l'Hôtel La Source
        """

        # Message HTML (optionnel mais recommandé)
        message_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0077b6, #00b4d8); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .section {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #0077b6; }}
                .section-title {{ color: #0077b6; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
                .info-row:last-child {{ border-bottom: none; }}
                .info-label {{ color: #6b7280; }}
                .info-value {{ font-weight: bold; color: #12202b; }}
                .price {{ font-size: 24px; color: #0077b6; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🏨 Hôtel La Source</h1>
                    <p style="margin: 10px 0 0 0;">Réservation Confirmée</p>
                </div>

                <div class="content">
                    <p>Bonjour <strong>{reservation.prenom} {reservation.nom}</strong>,</p>
                    <p>Nous avons le plaisir de vous confirmer votre réservation à l'Hôtel La Source.</p>

                    <div class="section">
                        <div class="section-title">📋 Détails de votre réservation</div>
                        <div class="info-row">
                            <span class="info-label">Numéro de réservation</span>
                            <span class="info-value">#{reservation.id}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Chambre</span>
                            <span class="info-value">{reservation.chambre.numero}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Type</span>
                            <span class="info-value">{reservation.chambre.get_type_display()}</span>
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-title">📅 Dates</div>
                        <div class="info-row">
                            <span class="info-label">Arrivée</span>
                            <span class="info-value">{reservation.date_arrivee.strftime('%d/%m/%Y')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Départ</span>
                            <span class="info-value">{reservation.date_depart.strftime('%d/%m/%Y')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Durée</span>
                            <span class="info-value">{nb_jours} nuit{"s" if nb_jours > 1 else ""}</span>
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-title">💰 Tarif</div>
                        <div style="text-align: center; padding: 20px 0;">
                            <div class="price">{prix_total:,.0f} Ar</div>
                            <p style="color: #6b7280; margin: 5px 0 0 0;">Prix total</p>
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-title">📍 Adresse & Contact</div>
                        <p style="margin: 5px 0;"><strong>Hôtel La Source</strong></p>
                        <p style="margin: 5px 0; color: #6b7280;">[Votre adresse complète]</p>
                        <p style="margin: 10px 0 5px 0;">📞 Téléphone : [Votre numéro]</p>
                        <p style="margin: 5px 0;">📧 Email : {settings.DEFAULT_FROM_EMAIL}</p>
                    </div>

                    <p style="margin-top: 20px;">Nous vous attendons avec impatience !</p>
                    <p><strong>L'équipe de l'Hôtel La Source</strong></p>
                </div>

                <div class="footer">
                    <p>Cet e-mail a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    <p>© 2024 Hôtel La Source - Tous droits réservés</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Envoi de l'e-mail
        email = EmailMultiAlternatives(
            subject=sujet,
            body=message_texte,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.email]
        )
        email.attach_alternative(message_html, "text/html")
        email.send(fail_silently=False)

        return True, "E-mail de confirmation envoyé avec succès."

    except Exception as e:
        return False, f"Erreur lors de l'envoi de l'e-mail : {str(e)}"


def envoyer_email_annulation_reservation(reservation):
    """Envoyer un e-mail d'annulation de réservation au client"""
    try:
        # Calcul des détails
        nb_jours = (reservation.date_depart - reservation.date_arrivee).days
        prix_total = nb_jours * reservation.chambre.prix

        # Sujet
        sujet = f"⚠️ Annulation de réservation - Hôtel La Source"

        # Message texte brut
        message_texte = f"""
Bonjour {reservation.prenom} {reservation.nom},

Nous vous informons que votre réservation à l'Hôtel La Source a été annulée.

📋 DÉTAILS DE LA RÉSERVATION ANNULÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Numéro de réservation : #{reservation.id}
Chambre : {reservation.chambre.numero}
Type : {reservation.chambre.get_type_display()}

📅 DATES INITIALEMENT PRÉVUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Arrivée : {reservation.date_arrivee.strftime('%d/%m/%Y')}
Départ : {reservation.date_depart.strftime('%d/%m/%Y')}
Durée : {nb_jours} nuit{"s" if nb_jours > 1 else ""}

Si vous n'êtes pas à l'origine de cette annulation ou si vous souhaitez effectuer une nouvelle réservation, n'hésitez pas à nous contacter.

📞 CONTACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Téléphone : [Votre numéro]
Email : {settings.DEFAULT_FROM_EMAIL}

Nous espérons vous accueillir prochainement.

Cordialement,
L'équipe de l'Hôtel La Source
        """

        # Message HTML
        message_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b, #ef4444); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .section {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #f59e0b; }}
                .section-title {{ color: #f59e0b; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
                .info-row:last-child {{ border-bottom: none; }}
                .info-label {{ color: #6b7280; }}
                .info-value {{ font-weight: bold; color: #12202b; }}
                .alert-box {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🏨 Hôtel La Source</h1>
                    <p style="margin: 10px 0 0 0;">Annulation de Réservation</p>
                </div>

                <div class="content">
                    <p>Bonjour <strong>{reservation.prenom} {reservation.nom}</strong>,</p>

                    <div class="alert-box">
                        <p style="margin: 0; font-weight: bold; color: #92400e;">⚠️ Votre réservation a été annulée</p>
                    </div>

                    <div class="section">
                        <div class="section-title">📋 Détails de la réservation annulée</div>
                        <div class="info-row">
                            <span class="info-label">Numéro de réservation</span>
                            <span class="info-value">#{reservation.id}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Chambre</span>
                            <span class="info-value">{reservation.chambre.numero}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Type</span>
                            <span class="info-value">{reservation.chambre.get_type_display()}</span>
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-title">📅 Dates initialement prévues</div>
                        <div class="info-row">
                            <span class="info-label">Arrivée</span>
                            <span class="info-value">{reservation.date_arrivee.strftime('%d/%m/%Y')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Départ</span>
                            <span class="info-value">{reservation.date_depart.strftime('%d/%m/%Y')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Durée</span>
                            <span class="info-value">{nb_jours} nuit{"s" if nb_jours > 1 else ""}</span>
                        </div>
                    </div>

                    <p style="margin-top: 20px;">Si vous n'êtes pas à l'origine de cette annulation ou si vous souhaitez effectuer une nouvelle réservation, n'hésitez pas à nous contacter.</p>

                    <div class="section">
                        <div class="section-title">📞 Contact</div>
                        <p style="margin: 5px 0;">Téléphone : [Votre numéro]</p>
                        <p style="margin: 5px 0;">Email : {settings.DEFAULT_FROM_EMAIL}</p>
                    </div>

                    <p>Nous espérons vous accueillir prochainement.</p>
                    <p><strong>L'équipe de l'Hôtel La Source</strong></p>
                </div>

                <div class="footer">
                    <p>Cet e-mail a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    <p>© 2024 Hôtel La Source - Tous droits réservés</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Envoi de l'e-mail
        email = EmailMultiAlternatives(
            subject=sujet,
            body=message_texte,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[reservation.email]
        )
        email.attach_alternative(message_html, "text/html")
        email.send(fail_silently=False)

        return True, "E-mail d'annulation envoyé avec succès."

    except Exception as e:
        return False, f"Erreur lors de l'envoi de l'e-mail : {str(e)}"


# ==================== DÉCORATEURS DE PERMISSIONS ====================

def is_admin(user):
    """Vérifier si l'utilisateur est admin"""
    return user.is_staff or user.is_superuser


def is_superuser_only(user):
    """Vérifier si l'utilisateur est superuser (pas juste staff)"""
    return user.is_superuser


def superuser_required(view_func):
    """Décorateur pour restreindre l'accès aux superusers uniquement"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "🚫 Action réservée aux administrateurs uniquement.")
            return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:dashboard'))
        return view_func(request, *args, **kwargs)
    return wrapper


# ==================== FONCTIONS UTILITAIRES ====================

def format_temps_relatif(dt):
    now = timezone.now()

    # Si dt est un datetime.date mais pas datetime.datetime
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())
        dt = timezone.make_aware(dt)

    diff = now - dt

    if diff.days == 0:
        return "Aujourd'hui", diff.total_seconds()
    elif diff.days == 1:
        return "Hier", diff.total_seconds()
    else:
        return f"Il y a {diff.days} jours", diff.total_seconds()


# ==================== AUTHENTIFICATION ====================

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard:dashboard')
        else:
            messages.error(request, "Vous n'avez pas les permissions d'accès à cette zone")
            return redirect('home')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    messages.success(request, f"Bienvenue {username} !")
                    return redirect('admin_dashboard:dashboard')
                else:
                    messages.error(request, "Vous n'avez pas les permissions pour accéder à cette zone.")
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    return render(request, 'admin/login.html', {
        'form': form,
        'next': request.GET.get('next')
    })


def admin_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('admin_dashboard:login')


# ==================== DASHBOARD ====================

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Vue principale du tableau de bord admin"""
    today = timezone.now().date()
    current_month = today.replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)

    # === STATISTIQUES DE BASE (visibles par tous) ===

    # Réservations actives (en cours ou à venir)
    reservations_actives = Reservation.objects.filter(
        Q(date_arrivee__lte=today, date_depart__gte=today) |  # En cours
        Q(date_arrivee__gt=today)  # À venir
    ).count()

    # Réservations actives du mois dernier
    reservations_actives_last_month = Reservation.objects.filter(
        Q(date_arrivee__lte=last_month, date_depart__gte=last_month) |
        Q(date_arrivee__gt=last_month, date_arrivee__lt=current_month)
    ).count()

    # Tendance réservations
    if reservations_actives_last_month > 0:
        tendance_reservations = round(
            ((reservations_actives - reservations_actives_last_month) / reservations_actives_last_month) * 100
        )
    else:
        tendance_reservations = 100 if reservations_actives > 0 else 0

    # Chambres occupées vs total
    chambres_total = Chambre.objects.filter(disponible=True).count()
    chambres_occupees = Reservation.objects.filter(
        date_arrivee__lte=today,
        date_depart__gte=today,
        confirmee=True
    ).values('chambre').distinct().count()

    # Tendance occupation
    chambres_occupees_last_month = Reservation.objects.filter(
        date_arrivee__lte=last_month,
        date_depart__gte=last_month,
        confirmee=True
    ).values('chambre').distinct().count()

    if chambres_occupees_last_month > 0:
        tendance_occupation = round(
            ((chambres_occupees - chambres_occupees_last_month) / chambres_occupees_last_month) * 100
        )
    else:
        tendance_occupation = 100 if chambres_occupees > 0 else 0

    # Note moyenne (simulée - à adapter avec un vrai modèle Avis)
    note_moyenne = 4.8
    tendance_note = -2

    # Réservations en attente
    reservations_en_attente = Reservation.objects.filter(confirmee=False).count()

    context = {
        # Stats principales (visibles par tous)
        'reservations_actives': reservations_actives,
        'tendance_reservations': abs(tendance_reservations),
        'tendance_reservations_type': 'up' if tendance_reservations >= 0 else 'down',

        'chambres_occupees': chambres_occupees,
        'chambres_total': chambres_total,
        'tendance_occupation': abs(tendance_occupation),
        'tendance_occupation_type': 'up' if tendance_occupation >= 0 else 'down',

        'note_moyenne': note_moyenne,
        'tendance_note': abs(tendance_note),
        'tendance_note_type': 'up' if tendance_note >= 0 else 'down',

        # Badge notifications
        'reservations_en_attente': reservations_en_attente,

        # Infos utilisateur
        'user': request.user,
    }

    # === DONNÉES RÉSERVÉES AUX SUPERUSERS ===
    if request.user.is_superuser:
        # Revenus du mois
        reservations_mois = Reservation.objects.filter(
            date_arrivee__month=today.month,
            date_arrivee__year=today.year,
            confirmee=True
        ).select_related('chambre')

        revenus_mois = Decimal('0')
        for resa in reservations_mois:
            nuits = (resa.date_depart - resa.date_arrivee).days
            revenus_mois += resa.chambre.prix * nuits

        # Revenus du mois dernier
        reservations_mois_dernier = Reservation.objects.filter(
            date_arrivee__month=last_month.month,
            date_arrivee__year=last_month.year,
            confirmee=True
        ).select_related('chambre')

        revenus_mois_dernier = Decimal('0')
        for resa in reservations_mois_dernier:
            nuits = (resa.date_depart - resa.date_arrivee).days
            revenus_mois_dernier += resa.chambre.prix * nuits

        # Tendance revenus
        if revenus_mois_dernier > 0:
            tendance_revenus = round(
                ((revenus_mois - revenus_mois_dernier) / revenus_mois_dernier) * 100
            )
        else:
            tendance_revenus = 100 if revenus_mois > 0 else 0

        context['revenus_mois'] = float(revenus_mois)
        context['tendance_revenus'] = abs(tendance_revenus)
        context['tendance_revenus_type'] = 'up' if tendance_revenus >= 0 else 'down'

        # === ACTIVITÉ RÉCENTE ===
        activites = []

        # Dernières réservations
        dernieres_reservations = Reservation.objects.select_related('chambre').order_by('-id')[:5]
        for resa in dernieres_reservations:
            temps_str, tri_valeur = format_temps_relatif(resa.created_at)
            activites.append({
                'type': 'reservation',
                'icon': 'blue',
                'titre': f"Nouvelle réservation - {resa.chambre.type}",
                'temps': temps_str,
                'tri': tri_valeur,
                'id': resa.id
            })

        # Check-out du jour
        checkouts_aujourdhui = Reservation.objects.filter(date_depart=today).select_related('chambre')
        for checkout in checkouts_aujourdhui:
            activites.append({
                'type': 'checkout',
                'icon': 'orange',
                'titre': f"Check-out effectué - Chambre {checkout.chambre.numero}",
                'temps': "Aujourd'hui",
                'tri': 0,
                'id': checkout.id
            })

        # Paiements récents
        paiements_recents = Reservation.objects.filter(payee=True).select_related('chambre').order_by('-id')[:3]
        for paiement in paiements_recents:
            date_reference = paiement.date_payee if paiement.date_payee else paiement.created_at
            temps_str, tri_valeur = format_temps_relatif(date_reference)
            nuits = (paiement.date_depart - paiement.date_arrivee).days
            montant = paiement.chambre.prix * nuits

            activites.append({
                'type': 'paiement',
                'icon': 'green',
                'titre': f"Paiement reçu - {montant:,.0f} Ar".replace(",", " "),
                'temps': temps_str,
                'tri': tri_valeur,
                'id': paiement.id
            })

        # Tri final
        activites = sorted(activites, key=lambda x: x['tri'])[:8]
        context['activites'] = activites

    return render(request, 'admin/dashboard.html', context)


# ==================== RÉSERVATIONS ====================

@login_required
@user_passes_test(is_admin)
def admin_reservations(request):
    """Liste de toutes les réservations avec filtres"""
    statut = request.GET.get('statut', 'toutes')
    recherche = request.GET.get('q', '')

    reservations = Reservation.objects.select_related('chambre').all()
    today = timezone.now().date()

    # Filtres
    if statut == 'actives':
        reservations = reservations.filter(
            date_arrivee__lte=today,
            date_depart__gte=today
        )
    elif statut == 'passees':
        reservations = reservations.filter(date_depart__lt=today)
    elif statut == 'attente':
        reservations = reservations.filter(confirmee=False)
    elif statut == 'payee':
        reservations = reservations.filter(payee=True)

    if recherche:
        reservations = reservations.filter(
            Q(nom__icontains=recherche) |
            Q(prenom__icontains=recherche) |
            Q(email__icontains=recherche) |
            Q(chambre__numero__icontains=recherche)
        )

    reservations = reservations.order_by('-date_arrivee')

    context = {
        'reservations': reservations,
        'statut_actuel': statut,
        'recherche': recherche,
        'user': request.user,
        'reservations_en_attente': Reservation.objects.filter(confirmee=False).count(),
    }

    return render(request, 'admin/reservations.html', context)


@login_required
@user_passes_test(is_admin)
def carte_reservation(request, reservation_id):
    reservations = get_object_or_404(
        Reservation.objects.select_related('chambre'),
        id=reservation_id
    )

    chambre = reservations.chambre

    # Calcul du nombre de jours
    jour1 = reservations.date_arrivee
    jour2 = reservations.date_depart
    nbJours = (jour2 - jour1).days

    # Prix total
    prix = nbJours * chambre.prix

    context = {
        'reservation': reservations,
        'user': request.user,
        'nbJours': nbJours,
        'prix': prix,
    }

    if request.method == 'GET':
        return render(request, 'admin/carte_reservations.html', context)

    if request.method == 'POST':
        action = request.POST.get('action')
        aujourdhui = timezone.now().date()

        # Vérification : client actuellement hébergé
        if reservations.date_arrivee == aujourdhui and reservations.confirmee == True and reservations.payee == True:
            messages.error(request, "🚫 Modification impossible : le client est actuellement hébergé.")
            return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

        # === ACTIONS AUTORISÉES POUR LES STAFF ===
        if action == 'confirmer_reservation':
            reservations.confirmee = True
            reservations.save()

            envoyer_email_confirmation_reservation(reservations)

            messages.success(request, "✅ Réservation confirmée et e-mail envoyé.")
            return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

        elif action == 'confirmer_payement':
            if not reservations.confirmee:
                messages.error(request, "⚠️ Impossible d'approuver le paiement avant la confirmation de la réservation.")
                return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

            reservations.payee = True
            reservations.date_payee = timezone.now()
            reservations.save()
            messages.success(request, "✅ Paiement confirmé avec succès.")
            return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

        # === ACTIONS RÉSERVÉES AUX SUPERUSERS ===
        elif action == 'annuler_payement':
            if not request.user.is_superuser:
                messages.error(request, "🚫 Action réservée aux administrateurs uniquement.")
                return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

            if not reservations.confirmee:
                messages.error(request, "⚠️ Impossible d'annuler le paiement avant la confirmation de la réservation.")
                return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

            reservations.payee = False
            reservations.save()
            messages.warning(request, "⚠️ Paiement annulé.")
            return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

        elif action == 'annuler_reservation':
            if not request.user.is_superuser:
                messages.error(request, "🚫 Action réservée aux administrateurs uniquement.")
                return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

            reservations.confirmee = False
            reservations.save()

            envoyer_email_annulation_reservation(reservations)

            messages.warning(request, "⚠️ Réservation annulée et e-mail envoyé.")
            return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

        elif action == 'supprimer_reservation':
            if not request.user.is_superuser:
                messages.error(request, "🚫 Action réservée aux administrateurs uniquement.")
                return redirect('admin_dashboard:carte_reservation', reservation_id=reservations.id)

            reservations.delete()
            messages.error(request, "❌ Réservation supprimée.")
            return redirect('admin_dashboard:reservations')


# ==================== CHAMBRES ====================

@login_required
@user_passes_test(is_admin)
def admin_chambres(request):
    """Liste de toutes les chambres (lecture seule pour staff)"""
    chambres = Chambre.objects.prefetch_related('images').all()

    stats_types = Chambre.objects.values('type').annotate(
        total=Count('id'),
        disponibles=Count('id', filter=Q(disponible=True))
    )

    context = {
        'chambres': chambres,
        'stats_types': stats_types,
        'user': request.user,
        'reservations_en_attente': Reservation.objects.filter(confirmee=False).count(),
    }

    return render(request, 'admin/chambres.html', context)


@login_required
@user_passes_test(is_admin)
@superuser_required
def ajouter_chambre(request):
    """Ajouter une chambre (réservé aux superusers)"""

    if request.method == 'POST':
        form = ChambreForm(request.POST)
        images = request.FILES.getlist('images')

        if form.is_valid():
            try:
                with transaction.atomic():
                    chambre = form.save()

                    images_ajoutees = 0
                    for img in images:
                        ChambreImage.objects.create(chambre=chambre, image=img)
                        images_ajoutees += 1

                    msg = f"✅ Chambre {chambre.numero} ajoutée avec succès"
                    if images_ajoutees > 0:
                        msg += f" avec {images_ajoutees} image(s)"
                    messages.success(request, msg + ".")

                    return redirect('admin_dashboard:chambres')

            except Exception as e:
                messages.error(request, f"❌ Erreur lors de l'ajout de la chambre : {str(e)}")
        else:
            messages.error(request, "⚠️ Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ChambreForm()

    context = {
        'form': form,
        'user': request.user,
        'reservations_en_attente': Reservation.objects.filter(confirmee=False).count(),
        'titre': 'Ajouter une chambre',
        'action': 'Ajouter',
    }

    return render(request, 'admin/ajouter_chambres.html', context)


@login_required
@user_passes_test(is_admin)
@superuser_required
def modifier_chambre(request, chambre_id):
    """Modifier une chambre existante (réservé aux superusers)"""

    chambre = get_object_or_404(Chambre, id=chambre_id)

    # Vérifier si la chambre a des réservations actives
    today = timezone.now().date()
    reservations_actives = Reservation.objects.filter(
        chambre=chambre,
        date_arrivee__lte=today,
        date_depart__gte=today,
        confirmee=True
    ).exists()

    if request.method == 'POST':
        form = ChambreForm(request.POST, instance=chambre)
        images = request.FILES.getlist('images')

        if form.is_valid():
            if reservations_actives and 'disponible' not in form.changed_data:
                messages.warning(
                    request,
                    "⚠️ Cette chambre est actuellement occupée. Seul le statut de disponibilité peut être modifié."
                )
            else:
                try:
                    with transaction.atomic():
                        chambre = form.save()

                        images_ajoutees = 0
                        for image in images:
                            ChambreImage.objects.create(chambre=chambre, image=image)
                            images_ajoutees += 1

                        msg = f"✅ Chambre {chambre.numero} modifiée avec succès"
                        if images_ajoutees > 0:
                            msg += f" ({images_ajoutees} nouvelle(s) image(s))"
                        messages.success(request, msg + ".")

                        return redirect('admin_dashboard:chambres')

                except Exception as e:
                    messages.error(request, f"❌ Erreur lors de la modification : {str(e)}")
        else:
            messages.error(request, "⚠️ Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ChambreForm(instance=chambre)

    context = {
        'form': form,
        'chambre': chambre,
        'user': request.user,
        'reservations_en_attente': Reservation.objects.filter(confirmee=False).count(),
        'reservations_actives': reservations_actives,
        'titre': f'Modifier la chambre {chambre.numero}',
        'action': 'Modifier'
    }

    return render(request, 'admin/ajouter_chambres.html', context)


@login_required
@user_passes_test(is_admin)
@superuser_required
def supprimer_chambre(request, chambre_id):
    """Supprimer une chambre (réservé aux superusers)"""

    chambre = get_object_or_404(Chambre, id=chambre_id)

    # Vérifier si la chambre a des réservations actives ou futures
    today = timezone.now().date()
    reservations_actives = Reservation.objects.filter(
        chambre=chambre,
        date_depart__gte=today
    ).exists()

    if reservations_actives:
        messages.error(
            request,
            f"❌ Impossible de supprimer la chambre {chambre.numero}. "
            "Elle a des réservations en cours ou à venir."
        )
        return redirect('admin_dashboard:chambres')

    if request.method == 'POST':
        numero = chambre.numero
        try:
            chambre.images.all().delete()
            chambre.delete()
            messages.success(request, f"✅ Chambre {numero} supprimée avec succès.")
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la suppression : {str(e)}")

        return redirect('admin_dashboard:chambres')

    return redirect('admin_dashboard:chambres')


@login_required
@user_passes_test(is_admin)
@superuser_required
def supprimer_image_chambre(request, image_id):
    """Supprimer une image de chambre (réservé aux superusers)"""

    image = get_object_or_404(ChambreImage, id=image_id)

    if image.chambre.images.count() <= 1:
        messages.error(request, "❌ Impossible de supprimer la dernière image de la chambre.")
    else:
        image.delete()
        messages.success(request, "✅ Image supprimée avec succès.")

    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:chambres'))


@login_required
@user_passes_test(is_admin)
@superuser_required
def toggle_disponibilite_chambre(request, chambre_id):
    """Activer/Désactiver la disponibilité d'une chambre (réservé aux superusers)"""
    chambre = get_object_or_404(Chambre, id=chambre_id)
    chambre.disponible = not chambre.disponible
    chambre.save()
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:chambres'))

@login_required
@user_passes_test(is_admin)
@superuser_required
def images_accueil(request):
    images = ImageAccueil.objects.all().order_by('-created_at')

    return render(request, 'admin/images_accueil.html', {'images': images})

def ajouter_image_accueil(request):
    if request.method == 'POST':
        form = ImageAccueilForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Image ajoutée avec succès !")
            return redirect('admin_dashboard:images_accueil')
    else:
        form = ImageAccueilForm()

    images = ImageAccueil.objects.all()
    return render(request, 'admin/images_accueil.html', {'form': form, 'images': images})

@login_required
@user_passes_test(is_admin)
@superuser_required
def toggle_image_actif(request, image_id):
    img = get_object_or_404(ImageAccueil, id=image_id)
    img.actif = not img.actif
    img.save()
    messages.success(request, f"L'image a été {'activée' if img.actif else 'désactivée'} !")
    return redirect('admin_dashboard:images_accueil')


@login_required
@user_passes_test(is_admin)
@superuser_required
def supprimer_image(request, image_id):
    img = get_object_or_404(ImageAccueil, id=image_id)
    if not img.actif:
        img.delete()
        messages.success(request, "Image supprimée avec succès !")
    else:
        messages.error(request, "Impossible de supprimer une image active !")
    return redirect('admin_dashboard:images_accueil')



# ==================== ACTIONS LEGACY (CONSERVÉES MAIS PROTÉGÉES) ====================

@login_required
@user_passes_test(is_admin)
def confirmer_reservation(request, reservation_id):
    """Confirmer une réservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.confirmee = True
    reservation.save()
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:dashboard'))


@login_required
@user_passes_test(is_admin)
@superuser_required
def annuler_reservation(request, reservation_id):
    """Annuler/Supprimer une réservation (réservé aux superusers)"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.delete()
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard:dashboard'))