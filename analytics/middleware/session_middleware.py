# analytics/middleware/session_middleware.py
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.backends.db import SessionStore
from django.contrib import messages
from django.conf import settings
import logging

logger = logging.getLogger('cgvbookstore')


class CustomSessionMiddleware(SessionMiddleware):
    """Processa a resposta do request e trata exceções de sessão interrompida"""

    def process_response(self, request, response):
        try:
            return super().process_response(request, response)
        except SessionInterrupted:
            logger.warning("Sessão interrompida detectada")

            if hasattr(request, 'user') and request.user.is_authenticated:
                logger.warning(f"Renovando sessão para usuário: {request.user.username}")
                request.session = SessionStore()
                request.session.create()

                messages.info(request, "Sua sessão foi renovada por motivos de segurança.")

                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    request.session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE
                )
                return response

            return super().process_response(request, response)

        except Exception as e:
            logger.error(f"Erro no middleware de sessão: {str(e)}")
            return response