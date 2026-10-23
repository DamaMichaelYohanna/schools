from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list_view, name='student_list'),
    path('create/', views.student_create_view, name='student_create'),
    path('<int:pk>/', views.student_detail_view, name='student_detail'),
    path('<int:pk>/edit/', views.student_edit_view, name='student_edit'),
]
