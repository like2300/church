from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime, date, timedelta
from .models import Member, Attendance, CulteSession, Church, GrowthConfig, AbsenceAlert, Location, UserProfile, Card, CulteType
from .forms import MemberForm, AttendanceForm, CardForm, CulteSessionForm


def user_is_admin(user):
    """Vérifie si l'utilisateur est ADMIN_CHURCH"""
    try:
        return user.profile.role == 'ADMIN_CHURCH'
    except UserProfile.DoesNotExist:
        return False


def login_view(request):
    """
    Page de connexion avec vérification de la paroisse.
    L'utilisateur doit sélectionner sa paroisse correspondant à son profil.
    """
    # Si déjà connecté, rediriger vers l'accueil
    if request.user.is_authenticated:
        return redirect('home')

    # Récupérer toutes les églises
    churches = Church.objects.select_related('location').all()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        church_id = request.POST.get('church')

        # Vérifier que la paroisse est sélectionnée
        if not church_id:
            messages.error(request, '⚠️ Veuillez sélectionner votre paroisse sur la carte ou dans la liste.')
            return render(request, 'registration/login.html', {'churches': churches})

        # Authentifier l'utilisateur
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                # Vérifier le profil utilisateur
                profile = user.profile
                selected_church = Church.objects.get(id=church_id)

                # Vérifier que la paroisse sélectionnée correspond au profil
                if profile.church == selected_church:
                    login(request, user)
                    messages.success(request, f'✅ Bienvenue {user.username} !')
                    return redirect('home')
                else:
                    messages.error(
                        request, 
                        f'❌ Votre paroisse est <b>{profile.church.name}</b> ({profile.church.location.name}). '
                        f'Veuillez sélectionner cette paroisse pour vous connecter.'
                    )
            except UserProfile.DoesNotExist:
                messages.error(request, '❌ Profil utilisateur non configuré. Contactez l\'administrateur.')
            except Church.DoesNotExist:
                messages.error(request, '❌ Paroisse invalide.')
        else:
            messages.error(request, '❌ Nom d\'utilisateur ou mot de passe incorrect.')

    return render(request, 'registration/login.html', {'churches': churches})


def logout_view(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    messages.info(request, '👋 Vous avez été déconnecté avec succès.')
    return redirect('login')


@login_required(login_url='login')
def home(request):
    """Page d'accueil avec statistiques - ADMIN seulement"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')

    # Récupérer l'église de l'admin connecté
    user_church = request.user.profile.church

    context = {
        'total_members': Member.objects.filter(church=user_church).count(),
        'visitors': Member.objects.filter(church=user_church, status='VISITOR').count(),
        'regular_members': Member.objects.filter(church=user_church, status='REGULAR').count(),
        'total_cultes': CulteSession.objects.filter(church=user_church).count(),
        'attendances_today': Attendance.objects.filter(member__church=user_church, recorded_at__date=timezone.now().date()).count(),
        'user_church': user_church,
    }
    return render(request, 'church/home.html', context)


@login_required(login_url='login')
def member_list(request):
    """Liste des membres - Filtré par église de l'utilisateur"""
    # Récupérer l'église de l'utilisateur connecté
    user_church = request.user.profile.church

    # Vérifier si export CSV demandé
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        members = Member.objects.filter(church=user_church).select_related('church')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="membres_{user_church.name}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Prénom', 'Nom', 'Genre', 'Téléphone', 'Statut', 'Église', 'Date adhésion'])
        for member in members:
            writer.writerow([
                member.first_name,
                member.last_name,
                member.get_genre_display(),
                member.phone or '',
                member.get_status_display(),
                member.church.name,
                member.date_joined.strftime('%d/%m/%Y')
            ])
        
        return response

    # Filtrer les membres de cette église uniquement avec annotation du nombre de présences
    from django.db.models import Count
    members = Member.objects.filter(
        church=user_church
    ).select_related('church').annotate(
        attendance_count=Count('history')
    )

    # Filtres
    status = request.GET.get('status')
    search = request.GET.get('search')

    if status:
        members = members.filter(status=status)
    if search:
        members = members.filter(
            first_name__icontains=search
        ) | members.filter(
            last_name__icontains=search
        )

    # Calculer les statistiques
    total = members.count()
    visitors = members.filter(status='VISITOR').count()
    regular = members.filter(status='REGULAR').count()

    context = {
        'members': members,
        'user_church': user_church,
        'total_members': total,
        'visitors_count': visitors,
        'regular_count': regular,
    }
    return render(request, 'church/member_list.html', context)


@login_required(login_url='login')
def member_create(request):
    """Créer un nouveau membre - Église pré-remplie automatiquement"""
    # Récupérer l'église de l'utilisateur connecté
    user_church = request.user.profile.church
    
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.church = user_church  # Force l'église de l'utilisateur
            member.save()
            messages.success(request, f'✅ Membre {member.first_name} {member.last_name} ajouté avec succès !')
            return redirect('member_list')
    else:
        form = MemberForm()
    
    return render(request, 'church/member_form.html', {
        'form': form, 
        'title': 'Nouveau Membre',
        'user_church': user_church
    })


@login_required(login_url='login')
def member_detail(request, pk):
    """Détail d'un membre avec historique de présences"""
    member = get_object_or_404(Member, pk=pk)
    # Use 'history' related_name (defined in Attendance model)
    attendances_qs = member.history.select_related('culte_session__culte_type').order_by('-recorded_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(attendances_qs, 10)  # 10 attendances per page
    page = request.GET.get('page', 1)
    attendances = paginator.get_page(page)

    context = {
        'member': member,
        'attendances': attendances,
        'page_obj': attendances,
        'is_paginated': paginator.num_pages > 1,
    }
    return render(request, 'church/member_detail.html', context)


@login_required(login_url='login')
def attendance_create(request):
    """Créer une présence pour un membre - Filtré par église"""
    user_church = request.user.profile.church
    selected_member = None
    selected_session = None
    selected_date = timezone.now().date()
    culte_sessions = []

    if request.method == 'POST':
        member_id = request.POST.get('member')
        culte_session_id = request.POST.get('culte_session')

        if member_id and culte_session_id:
            member = get_object_or_404(Member, pk=member_id, church=user_church)
            culte_session = get_object_or_404(CulteSession, pk=culte_session_id, church=user_church)

            # Vérifier si le membre est déjà présent pour cette session
            existing_attendance = Attendance.objects.filter(
                member=member,
                culte_session=culte_session
            ).first()

            if existing_attendance:
                messages.error(
                    request,
                    f'⚠️ {member.first_name} {member.last_name} est déjà présent(e) pour cette session de culte.'
                )
            else:
                attendance = Attendance.objects.create(member=member, culte_session=culte_session)
                messages.success(request, f'✅ Présence enregistrée pour {attendance.member.first_name} !')
                return redirect('member_detail', pk=attendance.member.pk)

    form = AttendanceForm()

    # Recherche de membre - limité à l'église de l'utilisateur
    search = request.GET.get('search', '')
    members = None
    if search:
        members = Member.objects.filter(church=user_church).filter(
            first_name__icontains=search
        ) | Member.objects.filter(church=user_church).filter(
            last_name__icontains=search
        )
        # Add pagination
        from django.core.paginator import Paginator
        paginator = Paginator(members.order_by('last_name', 'first_name'), 10)  # 10 members per page
        page = request.GET.get('page', 1)
        members = paginator.get_page(page)
    else:
        members = Member.objects.filter(church=user_church)[:10]

    # Get selected member info
    if request.GET.get('member_id'):
        selected_member = get_object_or_404(Member, pk=request.GET.get('member_id'))

    # Get date for filtering
    if request.GET.get('date'):
        selected_date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()

    # Get culte sessions for selected date and church
    if selected_date:
        culte_sessions = CulteSession.objects.filter(
            church=user_church,
            date__date=selected_date
        ).select_related('culte_type')

    context = {
        'form': form,
        'search': search,
        'members': members,
        'user_church': user_church,
        'selected_member': selected_member,
        'selected_date': selected_date,
        'culte_sessions': culte_sessions,
        'is_paginated': hasattr(members, 'has_next'),
        'page_obj': members if hasattr(members, 'has_next') else None,
    }
    return render(request, 'church/attendance_form.html', context)


@login_required(login_url='login')
def attendance_export(request):
    """Exporter l'historique des présences en CSV"""
    user_church = request.user.profile.church
    
    import csv
    from django.http import HttpResponse
    
    attendances = Attendance.objects.filter(
        member__church=user_church
    ).select_related('member', 'culte_session__culte_type').order_by('-culte_session__date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="presences_{user_church.name}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Membre', 'Type de Culte', 'Thème', 'Enregistré le'])
    for attendance in attendances:
        writer.writerow([
            attendance.culte_session.date.strftime('%d/%m/%Y %H:%M'),
            f'{attendance.member.first_name} {attendance.member.last_name}',
            attendance.culte_session.culte_type.name,
            attendance.culte_session.theme or '',
            attendance.recorded_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    return response


@login_required(login_url='login')
def alerts_export(request):
    """Exporter les alertes d'absence en CSV"""
    user_church = request.user.profile.church
    
    import csv
    from django.http import HttpResponse
    
    alerts = AbsenceAlert.objects.filter(
        church=user_church
    ).select_related('member', 'church').order_by('-created_at')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="alertes_{user_church.name}_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Membre', 'Église', 'Dernière présence', 'Créée le', 'Statut', 'Notes pastorales'])
    for alert in alerts:
        writer.writerow([
            f'{alert.member.first_name} {alert.member.last_name}',
            alert.church.name,
            alert.last_seen.strftime('%d/%m/%Y') if alert.last_seen else '',
            alert.created_at.strftime('%d/%m/%Y %H:%M'),
            'Résolu' if alert.is_resolved else 'En attente',
            alert.pastoral_notes or ''
        ])
    
    return response


@login_required(login_url='login')
def api_culte_sessions(request):
    """API endpoint to get culte sessions for a specific date - Filtré par église du user"""
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': 'Date required'}, status=400)

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        user_church = request.user.profile.church

        sessions = CulteSession.objects.filter(
            church=user_church,
            date__date=selected_date
        ).select_related('culte_type')

        # Format for display
        formatted_sessions = []
        for s in sessions:
            formatted_sessions.append({
                'id': s.id,
                'theme': s.theme or 'Sans thème',
                'officiant': s.officiant or 'Sans officiant',
                'culte_type': s.culte_type.name if s.culte_type else 'Culte'
            })

        return JsonResponse({'sessions': formatted_sessions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url='login')
def alerts_list(request):
    """Liste des alertes d'absence - ADMIN seulement, filtré par église"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')

    # Récupérer l'église de l'admin connecté
    user_church = request.user.profile.church
    
    # Générer les alertes d'absence automatiquement
    generate_absence_alerts(user_church)

    alerts = AbsenceAlert.objects.select_related('member', 'church').filter(
        church=user_church,
        is_resolved=False
    ).order_by('-created_at')
    
    # Récupérer la configuration pour afficher le seuil d'absence
    config = GrowthConfig.get_config()

    context = {
        'alerts': alerts,
        'user_church': user_church,
        'config': config
    }
    return render(request, 'church/alerts_list.html', context)


def generate_absence_alerts(user_church):
    """
    Génère automatiquement les alertes d'absence pour les membres actifs
    qui n'ont pas été vus depuis le seuil défini dans GrowthConfig.
    """
    config = GrowthConfig.get_config()
    absence_threshold = timezone.now() - timedelta(days=config.absence_limit_days)
    
    # Récupérer tous les membres actifs de l'église
    active_members = Member.objects.filter(
        church=user_church,
        status='REGULAR'
    ).select_related('church')
    
    for member in active_members:
        # Trouver la dernière présence du membre
        last_attendance = Attendance.objects.filter(
            member=member
        ).select_related('culte_session').order_by('-culte_session__date').first()
        
        if last_attendance is None:
            # Membre sans aucune présence - ne pas créer d'alerte
            continue
        
        # Vérifier si la dernière présence est plus ancienne que le seuil
        if last_attendance.culte_session.date < absence_threshold:
            # Vérifier si une alerte existe déjà pour ce membre
            existing_alert = AbsenceAlert.objects.filter(
                member=member,
                church=user_church,
                is_resolved=False
            ).first()
            
            if not existing_alert:
                # Créer une nouvelle alerte
                AbsenceAlert.objects.create(
                    church=user_church,
                    member=member,
                    last_seen=last_attendance.recorded_at
                )


@login_required(login_url='login')
def alert_resolve(request, alert_id):
    """Marquer une alerte d'absence comme résolue"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')
    
    alert = get_object_or_404(AbsenceAlert, pk=alert_id, church=request.user.profile.church)
    
    if request.method == 'POST':
        pastoral_notes = request.POST.get('pastoral_notes', '')
        alert.is_resolved = True
        alert.pastoral_notes = pastoral_notes
        alert.save()
        messages.success(request, f'✅ Alerte marquée comme résolue pour {alert.member.first_name} {alert.member.last_name}')
    
    return redirect('alerts_list')


@login_required(login_url='login')
def card_create(request, member_pk=None):
    """Créer une carte pour un membre - Filtré par église"""
    user_church = request.user.profile.church
    
    # Get member if pk provided
    member = None
    if member_pk:
        member = get_object_or_404(Member, pk=member_pk, church=user_church)
    
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            # Ensure member belongs to user's church
            if card.member.church != user_church:
                messages.error(request, '❌ Vous ne pouvez créer des cartes que pour les membres de votre église.')
                return redirect('member_list')
            card.save()
            messages.success(request, f'✅ Carte {card.card_number} créée pour {card.member.first_name} {card.member.last_name} !')
            return redirect('member_detail', pk=card.member.pk)
    else:
        form = CardForm()
        if member:
            form.fields['member'].initial = member

    # Get member's existing cards if viewing for specific member
    existing_cards = []
    if member:
        existing_cards = member.cards.all().order_by('-created_at')

    context = {
        'form': form,
        'member': member,
        'existing_cards': existing_cards,
        'user_church': user_church,
    }
    return render(request, 'church/card_form.html', context)


@login_required(login_url='login')
def culte_session_create(request):
    """Créer une session de culte - Filtré par église"""
    user_church = request.user.profile.church
    
    if request.method == 'POST':
        form = CulteSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.church = user_church  # Force l'église de l'utilisateur
            try:
                session.save()
                messages.success(request, f'✅ Session de culte "{session.theme}" créée pour le {session.date.strftime("%d %b %Y")} !')
                return redirect('home')
            except IntegrityError:
                messages.error(request, '⚠️ Une session de culte existe déjà pour ce type, cette date et votre église.')
    else:
        form = CulteSessionForm()

    context = {
        'form': form,
        'user_church': user_church,
    }
    return render(request, 'church/culte_session_form.html', context)


@login_required(login_url='login')
def culte_session_list(request):
    """Liste des sessions de culte avec statistiques - Filtré par église"""
    user_church = request.user.profile.church

    # Vérifier si export CSV demandé
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        sessions = CulteSession.objects.filter(
            church=user_church
        ).select_related('culte_type').order_by('-date')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="cultes_{user_church.name}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Thème', 'Officiant', 'Église'])
        for session in sessions:
            writer.writerow([
                session.date.strftime('%d/%m/%Y %H:%M'),
                session.culte_type.name,
                session.theme or '',
                session.officiant or '',
                session.church.name
            ])
        
        return response

    # Get all culte sessions for user's church
    sessions = CulteSession.objects.filter(church=user_church).select_related('culte_type').order_by('-date')

    # Filters
    culte_type = request.GET.get('culte_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if culte_type:
        sessions = sessions.filter(culte_type_id=culte_type)
    if date_from:
        sessions = sessions.filter(date__date__gte=date_from)
    if date_to:
        sessions = sessions.filter(date__date__lte=date_to)

    # Get culte types for filter dropdown
    culte_types = CulteType.objects.all()

    # Calculate statistics for each session
    sessions_with_stats = []
    total_presences = 0
    total_hommes = 0
    total_femmes = 0
    total_enfants = 0
    
    for session in sessions:
        stats = session.get_attendance_stats()

        # Count active members present
        active_present = Attendance.objects.filter(
            culte_session=session,
            member__status='REGULAR'
        ).count()

        # Count total active members in this church
        total_active = Member.objects.filter(church=user_church, status='REGULAR').count()

        # Calculate absent active members
        active_absent = total_active - active_present

        sessions_with_stats.append({
            'session': session,
            'total': stats['total'],
            'hommes': stats['hommes'],
            'femmes': stats['femmes'],
            'enfants': stats['enfants'],
            'actifs_presents': active_present,
            'actifs_absents': active_absent,
        })
        
        # Accumulate totals
        total_presences += stats['total'] or 0
        total_hommes += stats['hommes'] or 0
        total_femmes += stats['femmes'] or 0
        total_enfants += stats['enfants'] or 0

    context = {
        'sessions': sessions_with_stats,
        'culte_types': culte_types,
        'user_church': user_church,
        'selected_culte_type': culte_type,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'total_presences': total_presences,
        'total_hommes': total_hommes,
        'total_femmes': total_femmes,
        'total_enfants': total_enfants,
    }
    return render(request, 'church/culte_session_list.html', context)


@login_required(login_url='login')
def statistics(request):
    """Page de statistiques avancées - Réservée aux administrateurs"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')

    user_church = request.user.profile.church

    # Filtres
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    culte_type_id = request.GET.get('culte_type', '')

    # Période par défaut (30 derniers jours)
    if not date_from:
        date_from = (timezone.now().date() - timedelta(days=30)).isoformat()
    if not date_to:
        date_to = timezone.now().date().isoformat()

    # Base queryset filtrée
    sessions_qs = CulteSession.objects.filter(church=user_church)
    attendances_qs = Attendance.objects.filter(member__church=user_church)

    # Appliquer les filtres
    if date_from:
        sessions_qs = sessions_qs.filter(date__date__gte=date_from)
        attendances_qs = attendances_qs.filter(culte_session__date__date__gte=date_from)
    if date_to:
        sessions_qs = sessions_qs.filter(date__date__lte=date_to)
        attendances_qs = attendances_qs.filter(culte_session__date__date__lte=date_to)
    if culte_type_id:
        sessions_qs = sessions_qs.filter(culte_type_id=culte_type_id)
        attendances_qs = attendances_qs.filter(culte_session__culte_type_id=culte_type_id)

    # Statistiques générales
    total_members = Member.objects.filter(church=user_church).count()
    visitors = Member.objects.filter(church=user_church, status='VISITOR').count()
    regular_members = Member.objects.filter(church=user_church, status='REGULAR').count()
    total_cultes = sessions_qs.count()
    total_presences = attendances_qs.count()

    # Statistiques par genre
    hommes = Member.objects.filter(church=user_church, genre='H').count()
    femmes = Member.objects.filter(church=user_church, genre='F').count()
    enfants = Member.objects.filter(church=user_church, genre='E').count()

    # Statistiques par statut
    status_stats = {
        'VISITOR': visitors,
        'REGULAR': regular_members,
        'BAPTISED': Member.objects.filter(church=user_church, status='BAPTISED').count(),
        'ACTIVE': Member.objects.filter(church=user_church, status='ACTIVE').count(),
    }

    # Présences par culte type (pour diagramme)
    culte_types = CulteType.objects.all()
    presences_by_type = []
    for ct in culte_types:
        count = attendances_qs.filter(culte_session__culte_type=ct).count()
        presences_by_type.append({
            'name': ct.name,
            'count': count,
            'percentage': round((count / total_presences * 100) if total_presences > 0 else 0, 1)
        })

    # Présences par mois (pour diagramme)
    presences_by_month = []
    for i in range(11, -1, -1):
        month_date = timezone.now().date() - timedelta(days=i*30)
        month_name = month_date.strftime('%b')
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year+1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month+1, day=1) - timedelta(days=1)
        
        count = attendances_qs.filter(
            culte_session__date__date__gte=month_start,
            culte_session__date__date__lte=month_end
        ).count()
        presences_by_month.append({
            'month': month_name,
            'count': count
        })

    # Présences par semaine (pour diagramme - 4 dernières semaines)
    presences_by_week = []
    for i in range(3, -1, -1):
        week_end = timezone.now().date() - timedelta(days=i*7)
        week_start = week_end - timedelta(days=6)
        count = attendances_qs.filter(
            culte_session__date__date__gte=week_start,
            culte_session__date__date__lte=week_end
        ).count()
        presences_by_week.append({
            'week': f'S{i+1}',
            'count': count
        })

    # Taux de participation (présences / membres actifs)
    participation_rate = round((total_presences / regular_members * 100) if regular_members > 0 else 0, 1)

    context = {
        'total_members': total_members,
        'visitors': visitors,
        'regular_members': regular_members,
        'total_cultes': total_cultes,
        'total_presences': total_presences,
        'hommes': hommes,
        'femmes': femmes,
        'status_stats': status_stats,
        'presences_by_type': presences_by_type,
        'presences_by_month': presences_by_month,
        'presences_by_week': presences_by_week,
        'participation_rate': participation_rate,
        'culte_types': culte_types,
        'selected_culte_type': culte_type_id,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'user_church': user_church,
    }

    return render(request, 'church/statistics.html', context)


@login_required(login_url='login')
def statistics_export(request):
    """Export des statistiques en Excel, PDF ou DOCX"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')

    export_format = request.GET.get('format', 'pdf')
    user_church = request.user.profile.church

    # Récupérer les mêmes données que la vue statistics
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not date_from:
        date_from = (timezone.now().date() - timedelta(days=30)).isoformat()
    if not date_to:
        date_to = timezone.now().date().isoformat()

    total_members = Member.objects.filter(church=user_church).count()
    visitors = Member.objects.filter(church=user_church, status='VISITOR').count()
    regular_members = Member.objects.filter(church=user_church, status='REGULAR').count()
    hommes = Member.objects.filter(church=user_church, genre='M').count()
    femmes = Member.objects.filter(church=user_church, genre='F').count()
    
    sessions_qs = CulteSession.objects.filter(church=user_church, date__date__gte=date_from, date__date__lte=date_to)
    attendances_qs = Attendance.objects.filter(member__church=user_church)
    if date_from:
        attendances_qs = attendances_qs.filter(culte_session__date__date__gte=date_from)
    if date_to:
        attendances_qs = attendances_qs.filter(culte_session__date__date__lte=date_to)
    
    total_cultes = sessions_qs.count()
    total_presences = attendances_qs.count()
    participation_rate = round((total_presences / regular_members * 100) if regular_members > 0 else 0, 1)

    if export_format == 'excel':
        # Export Excel simple (CSV-like)
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="statistiques_{user_church.name}_{date_from}_to_{date_to}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['STATISTIQUES - ' + user_church.name])
        writer.writerow(['Période:', date_from, 'au', date_to])
        writer.writerow([])
        writer.writerow(['Membres', 'Total'])
        writer.writerow(['Total Membres', total_members])
        writer.writerow(['Visiteurs', visitors])
        writer.writerow(['Membres Actifs', regular_members])
        writer.writerow(['Hommes', hommes])
        writer.writerow(['Femmes', femmes])
        writer.writerow([])
        writer.writerow(['Cultes', 'Total'])
        writer.writerow(['Total Cultes', total_cultes])
        writer.writerow(['Total Présences', total_presences])
        writer.writerow(['Taux de Participation', f'{participation_rate}%'])
        
        return response
    
    elif export_format == 'docx':
        # Export DOCX simple (HTML-like)
        from django.http import HttpResponse
        
        content = f"""
        <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word'>
        <head><meta charset='utf-8'><title>Statistiques</title></head>
        <body>
            <h1>STATISTIQUES - {user_church.name}</h1>
            <p>Période: {date_from} au {date_to}</p>
            
            <h2>Membres</h2>
            <table border='1'>
                <tr><td>Total Membres</td><td>{total_members}</td></tr>
                <tr><td>Visiteurs</td><td>{visitors}</td></tr>
                <tr><td>Membres Actifs</td><td>{regular_members}</td></tr>
                <tr><td>Hommes</td><td>{hommes}</td></tr>
                <tr><td>Femmes</td><td>{femmes}</td></tr>
            </table>
            
            <h2>Cultes</h2>
            <table border='1'>
                <tr><td>Total Cultes</td><td>{total_cultes}</td></tr>
                <tr><td>Total Présences</td><td>{total_presences}</td></tr>
                <tr><td>Taux de Participation</td><td>{participation_rate}%</td></tr>
            </table>
        </body>
        </html>
        """
        
        response = HttpResponse(content_type='application/msword')
        response['Content-Disposition'] = f'attachment; filename="statistiques_{user_church.name}.doc"'
        response.write(content)
        return response
    
    else:  # pdf - on utilise l'impression navigateur
        messages.info(request, 'ℹ️ Pour exporter en PDF, utilisez la fonction d\'impression de votre navigateur (Ctrl+P)')
        return redirect('statistics')


@login_required(login_url='login')
def report_generate(request):
    """Générer un rapport administratif complet"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')

    user_church = request.user.profile.church

    # Filtres
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Période par défaut (30 derniers jours)
    if not date_from:
        date_from = (timezone.now().date() - timedelta(days=30)).isoformat()
    if not date_to:
        date_to = timezone.now().date().isoformat()

    # Collecte des données
    sessions_qs = CulteSession.objects.filter(
        church=user_church,
        date__date__gte=date_from,
        date__date__lte=date_to
    ).select_related('culte_type').order_by('-date')
    
    attendances_qs = Attendance.objects.filter(
        member__church=user_church,
        culte_session__date__date__gte=date_from,
        culte_session__date__date__lte=date_to
    )

    # Statistiques générales
    total_members = Member.objects.filter(church=user_church).count()
    visitors = Member.objects.filter(church=user_church, status='VISITOR').count()
    regular_members = Member.objects.filter(church=user_church, status='REGULAR').count()
    total_cultes = sessions_qs.count()
    total_presences = attendances_qs.count()

    # Statistiques par genre
    hommes = Member.objects.filter(church=user_church, genre='H').count()
    femmes = Member.objects.filter(church=user_church, genre='F').count()
    enfants = Member.objects.filter(church=user_church, genre='E').count()

    # Nouveaux membres durant la période
    new_members = Member.objects.filter(
        church=user_church,
        date_joined__gte=date_from,
        date_joined__lte=date_to
    ).count()

    # Présences par type de culte
    culte_types = CulteType.objects.all()
    presences_by_type = []
    for ct in culte_types:
        count = attendances_qs.filter(culte_session__culte_type=ct).count()
        presences_by_type.append({
            'name': ct.name,
            'count': count,
            'percentage': round((count / total_presences * 100) if total_presences > 0 else 0, 1)
        })

    # Cultes avec plus de fréquentation
    top_cultes = sessions_qs.annotate(
        attendance_count=Count('attendances')
    ).order_by('-attendance_count')[:5]

    # Taux de participation
    participation_rate = round((total_presences / regular_members * 100) if regular_members > 0 else 0, 1)

    # Alertes d'absence non résolues
    active_alerts = AbsenceAlert.objects.filter(
        church=user_church,
        is_resolved=False
    ).count()

    context = {
        'user_church': user_church,
        'date_from': date_from,
        'date_to': date_to,
        'total_members': total_members,
        'visitors': visitors,
        'regular_members': regular_members,
        'total_cultes': total_cultes,
        'total_presences': total_presences,
        'hommes': hommes,
        'femmes': femmes,
        'enfants': enfants,
        'new_members': new_members,
        'presences_by_type': presences_by_type,
        'top_cultes': top_cultes,
        'participation_rate': participation_rate,
        'active_alerts': active_alerts,
        'report_date': timezone.now().date(),
    }

    return render(request, 'church/report_generate.html', context)


@login_required(login_url='login')
def report_export_pdf(request):
    """Exporter le rapport en PDF (via impression navigateur)"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')

    # Rediriger vers la page de génération avec paramètre print
    return redirect('report_generate') + '?print=1'


@login_required(login_url='login')
def report_export_docx(request):
    """Exporter le rapport en DOCX"""
    if not user_is_admin(request.user):
        messages.error(request, '⚠️ Accès réservé aux administrateurs uniquement.')
        return redirect('member_list')

    user_church = request.user.profile.church
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if not date_from:
        date_from = (timezone.now().date() - timedelta(days=30)).isoformat()
    if not date_to:
        date_to = timezone.now().date().isoformat()

    # Collecte des données (similaire à report_generate)
    total_members = Member.objects.filter(church=user_church).count()
    visitors = Member.objects.filter(church=user_church, status='VISITOR').count()
    regular_members = Member.objects.filter(church=user_church, status='REGULAR').count()
    hommes = Member.objects.filter(church=user_church, genre='H').count()
    femmes = Member.objects.filter(church=user_church, genre='F').count()
    enfants = Member.objects.filter(church=user_church, genre='E').count()
    total_cultes = CulteSession.objects.filter(
        church=user_church,
        date__date__gte=date_from,
        date__date__lte=date_to
    ).count()
    total_presences = Attendance.objects.filter(
        member__church=user_church,
        culte_session__date__date__gte=date_from,
        culte_session__date__date__lte=date_to
    ).count()

    # Format DOCX avec en-tête et mise en forme professionnelle
    content = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' 
          xmlns:w='urn:schemas-microsoft-com:office:word'
          xmlns:x='urn:schemas-microsoft-com:office:excel'>
    <head>
        <meta charset='utf-8'>
        <title>Rapport Administratif - {user_church.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #1e3a8a; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
            h2 {{ color: #1e40af; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #3b82f6; color: white; }}
            tr:nth-child(even) {{ background-color: #f3f4f6; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .info {{ background-color: #eff6ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0; }}
            .footer {{ margin-top: 50px; text-align: center; font-size: 10px; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class='header'>
            <h1>RAPPORT ADMINISTRATIF</h1>
            <h2>{user_church.name}</h2>
            <p><strong>Période :</strong> du {date_from} au {date_to}</p>
            <p><strong>Date du rapport :</strong> {timezone.now().strftime('%d/%m/%Y à %H:%M')}</p>
        </div>

        <div class='info'>
            <p><strong>Église :</strong> {user_church.name}</p>
            <p><strong>Localisation :</strong> {user_church.location.name if user_church.location else 'N/A'}</p>
        </div>

        <h2>1. STATISTIQUES GÉNÉRALES</h2>
        <table>
            <tr><th>Indicateur</th><th>Valeur</th></tr>
            <tr><td>Total Membres</td><td>{total_members}</td></tr>
            <tr><td>Visiteurs</td><td>{visitors}</td></tr>
            <tr><td>Membres Actifs</td><td>{regular_members}</td></tr>
            <tr><td>Hommes</td><td>{hommes}</td></tr>
            <tr><td>Femmes</td><td>{femmes}</td></tr>
            <tr><td>Enfants</td><td>{enfants}</td></tr>
            <tr><td>Total Cultes</td><td>{total_cultes}</td></tr>
            <tr><td>Total Présences</td><td>{total_presences}</td></tr>
        </table>

        <h2>2. ANALYSE DES PRÉSENCES</h2>
        <p>Le taux de participation moyen est de <strong>{round((total_presences / regular_members * 100) if regular_members > 0 else 0, 1)}%</strong></p>

        <h2>3. CONCLUSION</h2>
        <p>Ce rapport présente les statistiques d'activité de l'église pour la période indiquée. 
        Pour toute question ou demande d'information complémentaire, veuillez contacter l'administration.</p>

        <div class='footer'>
            <p>Document généré automatiquement par D'avant Croissance - Système de Gestion Intelligente</p>
            <p>© {timezone.now().year} - Tous droits réservés</p>
        </div>
    </body>
    </html>
    """

    response = HttpResponse(content_type='application/msword')
    response['Content-Disposition'] = f'attachment; filename="Rapport_{user_church.name}_{date_from}_to_{date_to}.doc"'
    response.write(content)
    return response
