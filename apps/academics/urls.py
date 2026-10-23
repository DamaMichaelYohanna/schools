from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('classes/', views.class_list_view, name='class_list'),
    path('classes/create/', views.class_create_view, name='class_create'),
    path('classes/<int:pk>/', views.class_detail_view, name='class_detail'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('allocations/', views.allocation_list_view, name='allocation_list'),
    path('allocations/create/', views.allocation_create_view, name='allocation_create'),
    path('allocations/<int:pk>/delete/', views.allocation_delete_view, name='allocation_delete'),
    path('calendar/', views.academic_calendar_view, name='calendar'),
]
