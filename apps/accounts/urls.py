from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/create/', views.staff_create_view, name='staff_create'),
    path('staff/<int:pk>/', views.staff_detail_view, name='staff_detail'),
    path('staff/<int:pk>/edit/', views.staff_edit_view, name='staff_edit'),
]
