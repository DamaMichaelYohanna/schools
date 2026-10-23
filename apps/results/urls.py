from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('select/', views.score_sheet_select_view, name='select'),
    path('entry/', views.score_entry_sheet_view, name='entry'),
    path('broadsheet/<int:class_id>/', views.class_broadsheet_view, name='broadsheet'),
    path('report-card/<int:student_id>/', views.student_report_card_view, name='report_card'),
]
