# analytics/middleware/logging_middleware.py
import logging
import time
from django.utils import timezone

logger = logging.getLogger('cgvbookstore')


class LoggingMiddleware:
    """Middleware centralizado para logging do sistema"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Não processa se for recurso estático
        if self._is_static_request(request):
            return self.get_response(request)

        # Log da requisição
        start_time = time.time()
        self._log_request(request)

        response = self.get_response(request)

        # Log da resposta
        self._log_response(request, response, start_time)
        return response

    def _is_static_request(self, request):
        """Verifica se é uma requisição de arquivo estático"""
        return any(path in request.path for path in [
            '/static/',
            '/media/',
            '.js',
            '.css',
            '.ico'
        ])

    def _log_request(self, request):
        """Registra informações da requisição"""
        if hasattr(request, 'user'):
            user = request.user.username if request.user.is_authenticated else 'anonymous'
        else:
            user = 'unknown'

        logger.info(
            f"Request started - Path: {request.path}, "
            f"Method: {request.method}, User: {user}"
        )

    def _log_response(self, request, response, start_time):
        """Registra informações da resposta"""
        duration = time.time() - start_time

        # Status codes comuns
        SUCCESS = range(200, 300)
        REDIRECT = range(300, 400)
        CLIENT_ERROR = range(400, 500)
        SERVER_ERROR = range(500, 600)

        if response.status_code in SUCCESS:
            if '/livros/adicionar/' in request.path:
                logger.info(f"Book add successful - Path: {request.path}")
            elif '/livros/excluir/' in request.path:
                logger.info(f"Book delete successful - Path: {request.path}")
            elif '/api/recomendacoes/' in request.path:
                logger.info(f"Recommendations updated successfully")
            else:
                logger.info(
                    f"Request completed - Path: {request.path}, "
                    f"Status: {response.status_code}, "
                    f"Duration: {duration:.2f}s"
                )
        elif response.status_code in REDIRECT:
            # Não loga redirecionamentos, pois são comportamentos normais
            pass
        elif response.status_code in CLIENT_ERROR:
            logger.warning(
                f"Client error - Path: {request.path}, "
                f"Status: {response.status_code}"
            )
        elif response.status_code in SERVER_ERROR:
            logger.error(
                f"Server error - Path: {request.path}, "
                f"Status: {response.status_code}"
            )
        else:
            logger.warning(
                f"Unknown status code - Path: {request.path}, "
                f"Status: {response.status_code}"
            )

    def _get_request_details(self, request):
        """Obtém detalhes relevantes da requisição para logging"""
        return {
            'path': request.path,
            'method': request.method,
            'user': request.user.username if hasattr(request,
                                                     'user') and request.user.is_authenticated else 'anonymous',
            'ip': self._get_client_ip(request),
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')