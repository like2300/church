from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('members/', views.member_list, name='member_list'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('cards/create/', views.card_create, name='card_create'),
    path('cards/create/<int:member_pk>/', views.card_create, name='card_create_for_member'),
    path('attendance/', views.attendance_create, name='attendance_create'),
    path('attendance/export/', views.attendance_export, name='attendance_export'),
    path('culte-sessions/create/', views.culte_session_create, name='culte_session_create'),
    path('culte-sessions/', views.culte_session_list, name='culte_session_list'),
    path('api/culte-sessions/', views.api_culte_sessions, name='api_culte_sessions'),
    path('alerts/', views.alerts_list, name='alerts_list'),
    path('alerts/export/', views.alerts_export, name='alerts_export'),
    path('alerts/<int:alert_id>/resolve/', views.alert_resolve, name='alert_resolve'),
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/export/', views.statistics_export, name='statistics_export'),
    path('report/generate/', views.report_generate, name='report_generate'),
    path('report/export/pdf/', views.report_export_pdf, name='report_export_pdf'),
    path('report/export/docx/', views.report_export_docx, name='report_export_docx'),
]
