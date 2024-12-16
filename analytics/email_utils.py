# analytics/email_utils.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings as django_settings


def send_analytics_report_email(to_email, report_data):
    """Envia email com relatório diário de analytics."""
    subject = f'Relatório Analytics - {report_data["date"]}'

    # Renderiza o template do email
    html_message = render_to_string('analytics/email/daily_report.html', {
        'data': report_data
    })

    # Versão texto plano do email
    text_message = f"""
    Relatório de Analytics - {report_data['date']}

    Visitas Totais: {report_data['total_visits']}
    Visitas Autenticadas: {report_data['authenticated_visits']}
    Visitas Anônimas: {report_data['anonymous_visits']}
    Usuários Ativos: {report_data['active_users']}
    """

    try:
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False