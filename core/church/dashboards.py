from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.views import UnfoldModelAdminViewMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q
from .models import Member, Attendance, CulteSession, Church, AbsenceAlert


@staff_member_required
def custom_dashboard(request):
    """Custom dashboard with statistics"""
    
    # Statistics
    total_members = Member.objects.count()
    total_churches = Church.objects.count()
    total_cultes = CulteSession.objects.count()
    total_attendances = Attendance.objects.count()
    active_alerts = AbsenceAlert.objects.filter(is_resolved=False).count()
    
    # Members by status
    visitors = Member.objects.filter(status='VISITOR').count()
    regular_members = Member.objects.filter(status='REGULAR').count()
    
    # Members by genre
    men = Member.objects.filter(genre='H').count()
    women = Member.objects.filter(genre='F').count()
    children = Member.objects.filter(genre='E').count()
    
    # Recent attendances
    recent_attendances = Attendance.objects.select_related('member', 'culte_session').order_by('-recorded_at')[:10]
    
    # Top churches
    top_churches = Church.objects.annotate(
        member_count=Count('members')
    ).order_by('-member_count')[:5]
    
    context = {
        "total_members": total_members,
        "total_churches": total_churches,
        "total_cultes": total_cultes,
        "total_attendances": total_attendances,
        "active_alerts": active_alerts,
        "visitors": visitors,
        "regular_members": regular_members,
        "men": men,
        "women": women,
        "children": children,
        "recent_attendances": recent_attendances,
        "top_churches": top_churches,
        **getattr(request, 'site_profile', {}),
    }
    
    return render(request, "admin/custom_dashboard.html", context)
