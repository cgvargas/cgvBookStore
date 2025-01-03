# analytics/analytics_middleware.py
from django.conf import settings
from django.contrib.auth import logout

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.backends.db import SessionStore
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
import time
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.cache import cache
from user_agents import parse
import logging

from analytics.models import SiteAnalytics, PageView, UserActivityLog

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CustomSessionMiddleware(SessionMiddleware):
    """
    Processa a resposta do request e trata exceções de sessão interrompida.
    """
    def process_response(self, request, response):
        try:
            return super().process_response(request, response)
        except SessionInterrupted:
            logger.warning("Sessão interrompida detectada")

            if hasattr(request, 'user') and request.user.is_authenticated:
                logger.warning("Usuário autenticado com sessão interrompida")

                # Ao invés de forçar logout, tenta recuperar a sessão
                request.session = SessionStore()
                request.session.create()

                # Preserva a autenticação do usuário
                from django.contrib.auth import login
                login(request, request.user)

                # Adiciona mensagem de aviso
                messages.info(request, "Sua sessão foi renovada por motivos de segurança.")

                # Retorna a resposta original com a nova sessão
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
            logger.error(f"Erro no middleware de sessão: {str(e)}", exc_info=True)
            return response

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Logs para requisições de exclusão
            if 'livros/excluir' in request.path:
                logger.debug("\n=== Detalhes da requisição de exclusão de livro ===")
                logger.debug(f"Path: {request.path}")
                logger.debug(f"Method: {request.method}")
                logger.debug(f"User: {request.user}")
                logger.debug(f"Headers: {dict(request.headers)}")
                logger.debug(f"Content Type: {request.content_type}")
                logger.debug(f"POST data: {request.POST}")

            # Marca o tempo inicial
            request.start_time = time.time()
            response = self.get_response(request)

            # Logs da resposta para exclusão
            if 'livros/excluir' in request.path:
                logger.debug("\n=== Detalhes da resposta de exclusão ===")
                logger.debug(f"Status Code: {response.status_code}")
                logger.debug(f"Content Type: {response.get('Content-Type', 'não definido')}")
                try:
                    if 'application/json' in response.get('Content-Type', ''):
                        import json
                        content = json.loads(response.content.decode('utf-8'))
                        logger.debug(f"Response Content: {content}")
                except Exception as e:
                    logger.debug(f"Erro ao decodificar resposta: {str(e)}")

            # Verifica se deve rastrear
            if not self.should_track_request(request):
                return response

            # Verifica se é um refresh ou uma visita recente do mesmo usuário/sessão
            if AnalyticsMiddleware._is_duplicate_visit(request):
                return response

            # Processa a visita
            self._process_visit(request)
            return response

        except Exception as e:
            logger.error(f"Erro no Analytics Middleware: {str(e)}")
            return self.get_response(request)

    @staticmethod
    def _is_duplicate_visit(request):
        """Verifica se é uma visita duplicada."""
        try:
            # Chave única para o usuário/sessão
            visitor_key = request.user.id if request.user.is_authenticated else request.session.session_key

            # Chave do cache apenas para o visitante
            cache_key = f'visitor_{visitor_key}'

            # Verifica se já existe uma visita recente (últimos 30 minutos)
            if cache.get(cache_key):
                return True

            # Marca esta visita no cache por 30 minutos
            cache.set(cache_key, True, 1800)  # 1800 segundos = 30 minutos
            return False

        except Exception as e:
            logger.error(f"Erro ao verificar visita duplicada: {str(e)}")
            return False

    def _process_visit(self, request):
        """Processa uma nova visita."""
        try:
            user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))

            # Registra a visualização da página
            page_view = PageView(
                url=request.path,
                usuario=request.user if request.user.is_authenticated else None,
                sessao_id=request.session.session_key or '',
                dispositivo=self._get_device_info(user_agent),
                navegador=self._get_browser_info(user_agent),
                tempo_na_pagina=timezone.timedelta(
                    seconds=time.time() - request.start_time
                )
            )
            page_view.save()

            # Atualiza as métricas diárias
            self._update_daily_analytics(request)

        except Exception as e:
            logger.error(f"Erro ao processar visita: {str(e)}")

    @staticmethod
    def should_track_request(request):
        """Determina se a requisição deve ser rastreada"""
        # Log específico para requisições de exclusão
        if 'livros/excluir' in request.path:
            logger.debug(f"\n=== Verificando rastreamento para exclusão ===")
            logger.debug(f"Path completo: {request.path}")
            logger.debug(f"Método: {request.method}")

        excluded_paths = [
            '/static/',
            '/admin/',
            '/media/',
            '/analytics/api/',
            '/api/',
            '/check-username/',
            '/logout/',
            '.css',
            '.js',
            '.ico',
            'favicon',
            'livros/excluir'  # Adicionado para não rastrear requisições de exclusão
        ]

        # Verifica se é AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if 'livros/excluir' in request.path and is_ajax:
            logger.debug("Requisição de exclusão é AJAX")

        # Verifica caminhos excluídos
        is_excluded = any(
            request.path.startswith(path) or
            (path.startswith('.') and request.path.endswith(path))
            for path in excluded_paths
        )
        if 'livros/excluir' in request.path and is_excluded:
            logger.debug("Caminho de exclusão está na lista de excluídos")

    @staticmethod
    def _get_device_info(user_agent):
        """Obtém informações detalhadas do dispositivo"""
        if user_agent.is_mobile:
            device_type = 'mobile'
        elif user_agent.is_tablet:
            device_type = 'tablet'
        elif user_agent.is_pc:
            device_type = 'desktop'
        else:
            device_type = 'other'

        # Ajusta a versão do Windows se necessário
        os_info = f"{user_agent.os.family}"
        if 'Windows' in os_info:
            # Mapeia a versão do Windows corretamente
            windows_version_map = {
                '10.0': '11',  # Windows 11 é reportado como 10.0 em alguns casos
                '6.3': '8.1',
                '6.2': '8',
                '6.1': '7'
            }

            os_version = user_agent.os.version_string
            if os_version in windows_version_map:
                os_info = f"Windows {windows_version_map[os_version]}"
            else:
                os_info = f"Windows {user_agent.os.version_string}"

        return {
            'type': device_type,
            'brand': user_agent.device.brand or 'unknown',
            'model': user_agent.device.model or 'unknown',
            'os': os_info.strip()
        }

    @staticmethod
    def _get_browser_info(user_agent):
        """Obtém informações detalhadas do navegador"""
        return {
            'family': user_agent.browser.family,
            'version': user_agent.browser.version_string,
            'bot': user_agent.is_bot
        }

    @staticmethod
    def _is_page_refresh(request):
        """
        Verifica se é uma atualização de página ou novo acesso
        """
        try:
            # Verifica o cabeçalho Cache-Control
            cache_control = request.META.get('HTTP_CACHE_CONTROL', '').lower()

            # Verifica o referrer e URL atual
            current_path = request.path
            referrer = request.META.get('HTTP_REFERER', '')

            # Extrai apenas o path do referrer (remove domínio)
            if referrer:
                from urllib.parse import urlparse
                referrer_path = urlparse(referrer).path
            else:
                referrer_path = ''

            # É refresh apenas se:
            # 1. O referrer path é igual ao path atual (mesma página)
            # 2. E tem indicadores de refresh nos headers
            is_refresh = (
                    current_path == referrer_path and
                    ('no-cache' in cache_control or 'max-age=0' in cache_control)
            )

            return is_refresh

        except Exception as e:
            logger.error(f"Erro ao verificar refresh: {str(e)}")
            return False

    @staticmethod
    def _update_daily_analytics(request):
        """Atualiza as métricas diárias"""
        try:
            today = timezone.now().date()
            analytics = SiteAnalytics.objects.get_or_create(data=today)[0]

            logger.debug(f"Estado anterior - Visitas: {analytics.visitas_total}, "
                         f"Autenticadas: {analytics.visitas_autenticadas}, "
                         f"Anônimas: {analytics.visitas_anonimas}")

            # Chave única para sessão
            session_key = request.session.session_key
            user_id = request.user.id if request.user.is_authenticated else None

            # Chaves para cache
            day_key = today.strftime('%Y-%m-%d')
            session_visit_key = f'visit_{session_key}_{day_key}'
            user_visit_key = f'visit_{user_id}_{day_key}' if user_id else None

            # Verifica se é uma visita pós-login
            is_post_login = request.session.get('authenticated_visit', False)

            if request.user.is_authenticated:
                if is_post_login:
                    # Se é um login recente, converte a visita de anônima para autenticada
                    request.session['authenticated_visit'] = False  # Reset o flag
                    if cache.get(session_visit_key):
                        analytics.visitas_anonimas = max(0, analytics.visitas_anonimas - 1)
                        analytics.visitas_autenticadas += 1
                        cache.delete(session_visit_key)
                        cache.set(user_visit_key, True, 86400)
                        logger.debug("Convertendo visita anônima para autenticada")
                elif not cache.get(user_visit_key) and not cache.get(session_visit_key):
                    # Nova visita autenticada
                    analytics.visitas_autenticadas += 1
                    analytics.visitas_total += 1
                    cache.set(user_visit_key, True, 86400)
                    logger.debug("Nova visita autenticada")
            else:
                if not cache.get(session_visit_key):
                    # Nova visita anônima
                    analytics.visitas_anonimas += 1
                    analytics.visitas_total += 1
                    cache.set(session_visit_key, True, 86400)
                    logger.debug("Nova visita anônima")

            # Atualiza usuários ativos
            active_users = UserActivityLog.objects.filter(
                timestamp__date=today,
                acao='login'
            ).values('usuario').distinct().count()
            analytics.usuarios_ativos = active_users

            analytics.save()

            logger.debug(f"Estado atual - Visitas: {analytics.visitas_total}, "
                         f"Autenticadas: {analytics.visitas_autenticadas}, "
                         f"Anônimas: {analytics.visitas_anonimas}")

        except Exception as e:
            logger.error(f"Erro ao atualizar analytics: {str(e)}")

    @staticmethod
    def _log_user_activity(request, user_agent):
        """Registra atividade detalhada do usuário"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return

        if not request.user.is_authenticated:
            return

        is_refresh = AnalyticsMiddleware._is_page_refresh(request)  # Mudou de self para AnalyticsMiddleware

        UserActivityLog.objects.create(
            usuario=request.user,
            acao='page_refresh' if is_refresh else 'page_view',
            detalhes={
                'url': request.path,
                'method': request.method,
                'referrer': request.META.get('HTTP_REFERER', ''),
                'device': AnalyticsMiddleware._get_device_info(user_agent),  # Mudou de self para AnalyticsMiddleware
                'browser': AnalyticsMiddleware._get_browser_info(user_agent),
                'is_refresh': is_refresh
            },
            ip_address=AnalyticsMiddleware._get_client_ip(request),
            secao_atual=request.path.split('/')[1] if request.path != '/' else 'home'
        )

    @staticmethod
    def _get_client_ip(request):
        """Obtém o IP real do cliente mesmo atrás de proxy"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class ImprovedAutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Não processa se estiver na página de login ou for uma requisição de recursos estáticos
        if (request.path == settings.LOGIN_URL or
                request.path.startswith('/static/') or
                request.path.startswith('/media/')):
            return self.get_response(request)

        if request.user.is_authenticated:
            try:
                current_time = timezone.now().timestamp()
                last_activity = request.session.get('last_activity')

                # Atualiza o timestamp da última atividade
                request.session['last_activity'] = current_time

                if last_activity:
                    idle_time = current_time - float(last_activity)
                    timeout = getattr(settings, 'SESSION_COOKIE_AGE', 86400)

                    if idle_time > timeout:
                        logger.info(f"Sessão expirada por inatividade para o usuário: {request.user.username}")
                        logout(request)
                        request.session.flush()

                        # Se for AJAX, retorna 401
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Sua sessão expirou por inatividade.',
                                'code': 'session_timeout'
                            }, status=401)

                        # Se não for AJAX e não estiver já na página de login
                        if request.path != settings.LOGIN_URL:
                            messages.warning(request,
                                             'Sua sessão expirou por inatividade. Por favor, faça login novamente.')
                            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

                # Verifica se o navegador foi fechado
                browser_closed = request.session.get('browser_closed', False)
                if browser_closed:
                    logger.info(f"Browser fechado detectado para usuário: {request.user.username}")
                    logout(request)
                    request.session.flush()
                    return redirect(settings.LOGIN_URL)

            except Exception as e:
                logger.error(f"Erro no middleware de auto logout: {str(e)}")

        response = self.get_response(request)
        return response
# Conecta aos sinais de login/logout
def on_user_logged_in(sender, request, user, **kwargs):
    try:
        today = timezone.now().date()
        analytics = SiteAnalytics.objects.get(data=today)

        # Verifica se o usuário já foi contado como anônimo hoje
        session_key = request.session.session_key
        if session_key:
            daily_anon_key = f'daily_visitor_{session_key}_{today}'
            if cache.get(daily_anon_key):
                # Ajusta as contagens: -1 anônimo, +1 autenticado
                analytics.visitas_anonimas = max(0, analytics.visitas_anonimas - 1)
                analytics.visitas_autenticadas += 1
                analytics.save()

                # Remove a marca de anônimo e adiciona como autenticado
                cache.delete(daily_anon_key)
                cache.set(f'daily_visitor_{user.id}_{today}', True, 86400)

    except SiteAnalytics.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Erro ao ajustar contagens após login: {str(e)}")

    # Continua com o registro normal de atividade
    UserActivityLog.objects.create(
        usuario=user,
        acao='login',
        detalhes={'method': 'form_login'},
        ip_address=request.META.get('REMOTE_ADDR')
    )


def on_user_logged_out(sender, request, user, **kwargs):
    if user:  # user pode ser None em alguns casos
        UserActivityLog.objects.create(
            usuario=user,
            acao='logout',
            detalhes={'method': 'user_initiated'},
            ip_address=request.META.get('REMOTE_ADDR')
        )


# Registra os handlers dos sinais
user_logged_in.connect(on_user_logged_in)
user_logged_out.connect(on_user_logged_out)