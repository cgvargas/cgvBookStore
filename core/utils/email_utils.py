# core/utils/email_utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_email_contato(dados_contato):
    """Envia e-mails relacionados ao contato (para admin e cliente)."""
    try:
        # E-mail para o administrador
        corpo_email_admin = f"""
        Nova mensagem de contato recebida:

        Nome: {dados_contato['nome']}
        Email: {dados_contato['email']}
        Assunto: {dados_contato['assunto']}

        Mensagem:
        {dados_contato['mensagem']}
        """

        # Envia para o admin
        send_mail(
            subject=f'Nova mensagem de {dados_contato["nome"]}: {dados_contato["assunto"]}',
            message=corpo_email_admin,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin[1] for admin in settings.ADMINS],
            fail_silently=False,
        )

        # Resposta automática para o cliente
        corpo_email_cliente = render_to_string('emails/confirmacao_contato.html', {
            'nome': dados_contato['nome'],
            'assunto': dados_contato['assunto']
        })

        # Envia resposta automática
        send_mail(
            subject='Confirmação de Recebimento - CG.BookStore',
            message='Recebemos sua mensagem. Em breve entraremos em contato.',  # Versão texto plano
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[dados_contato['email']],
            fail_silently=False,
            html_message=corpo_email_cliente  # Versão HTML
        )

        logger.info(f"E-mails enviados com sucesso para {dados_contato['email']}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar e-mails: {str(e)}")
        return False