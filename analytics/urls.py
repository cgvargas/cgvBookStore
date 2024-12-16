# analytics/urls.py

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Views principais
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('reset/', views.reset_analytics, name='reset_analytics'),

    # APIs para dados
    path('api/data/', views.get_analytics_data, name='api_data'),
    path('api/devices/', views.get_devices_data, name='get_devices'),
    path('api/books/', views.get_books_data, name='get_books'),
    path('api/trends/', views.get_trend_data, name='get_trends'),

    # Exportação
    path('export/excel/', views.export_excel_report, name='export_excel'),
    path('export/csv/', views.export_csv_report, name='export_csv'),
    path('export/pdf/', views.export_pdf_report, name='export_pdf'),

    # Configurações
    path('settings/', views.analytics_settings, name='settings'),

    # Modals
    path('api/visit-details/', views.get_visit_details, name='visit_details'),
]