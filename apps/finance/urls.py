from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.finance_dashboard_view, name='dashboard'),
    path('invoices/', views.invoices_list_view, name='invoices_list'),
    path('invoices/<int:pk>/', views.invoice_detail_view, name='invoice_detail'),
    path('generate-invoices/', views.generate_invoices_view, name='generate_invoices'),
    path('record-payment/', views.record_payment_view, name='record_payment'),
    path('receipt/<int:pk>/', views.receipt_view, name='receipt'),
    path('fee-structures/', views.fee_structures_view, name='fee_structures'),
]
