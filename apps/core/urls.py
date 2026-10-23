from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('settings/', views.school_settings_view, name='settings'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
]
