from django.utils import timezone
from datetime import timedelta
from .models import AbsenceAlert, Member, Attendance


def sidebar_data(request):
    """
    Context processor pour ajouter les données de la sidebar
    """
    data = {
        'alert_count': 0,
    }
    
    if request.user.is_authenticated:
        try:
            user_church = request.user.profile.church
            # Compter les alertes non résolues
            data['alert_count'] = AbsenceAlert.objects.filter(
                church=user_church,
                is_resolved=False
            ).count()
        except Exception:
            # Si l'utilisateur n'a pas de profil ou d'église
            data['alert_count'] = 0
    
    return data
