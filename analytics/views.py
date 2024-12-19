# analytics/views.py
import io
import traceback
import logging
import csv
import pandas as pd
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render
import json
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta, time

from django.views.decorators.csrf import ensure_csrf_cookie

from .email_utils import send_analytics_report_email
from .utils import AnalyticsProcessor
from .models import (SiteAnalytics, PageView, BookAnalytics, UserActivityLog,
                     AnalyticsSettings, SearchAnalytics, ErrorLog)
from .pdf_generator import generate_analytics_pdf
from django.views.decorators.http import require_POST


# Configuração do logger
logger = logging.getLogger(__name__)


def is_analytics_admin(user):
    """Verifica se o usuário tem permissão para acessar o analytics."""
    return user.is_superuser and user.groups.filter(name='Analytics_Admin').exists()

@login_required
@user_passes_test(is_analytics_admin)
def analytics_dashboard(request):
    """View principal do dashboard."""
    context = {
        'is_analytics_admin': True,
        'page_title': 'Dashboard Analytics'
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
@user_passes_test(is_analytics_admin)
def get_analytics_data(request):
    """API endpoint para dados gerais do analytics."""
    try:
        # Verifica se a requisição é AJAX
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({'error': 'Requisição inválida'}, status=400)

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Busca dados do analytics
        analytics_data = SiteAnalytics.objects.filter(
            data__range=[start_date, end_date]
        )

        # Processa dados de tendência
        trend_data = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = analytics_data.filter(data=current_date).first()
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'total': daily_data.visitas_total if daily_data else 0,
                'authenticated': daily_data.visitas_autenticadas if daily_data else 0,
                'anonymous': daily_data.visitas_anonimas if daily_data else 0,
                'active_users': daily_data.usuarios_ativos if daily_data else 0
            })
            current_date += timedelta(days=1)

        # Processa dados de dispositivos
        page_views = PageView.objects.filter(
            timestamp__date__range=[start_date, end_date]
        )
        devices_data = {}
        for view in page_views:
            try:
                device_info = view.dispositivo
                if isinstance(device_info, str):
                    device_info = json.loads(device_info)
                device_type = device_info.get('type', 'other')
                devices_data[device_type] = devices_data.get(device_type, 0) + 1
            except:
                devices_data['other'] = devices_data.get('other', 0) + 1

        # Calcula métricas principais
        main_metrics = {
            'total_visits': analytics_data.aggregate(Sum('visitas_total'))['visitas_total__sum'] or 0,
            'active_users': analytics_data.aggregate(Sum('usuarios_ativos'))['usuarios_ativos__sum'] or 0,
            'authenticated_visits': analytics_data.aggregate(Sum('visitas_autenticadas'))['visitas_autenticadas__sum'] or 0,
            'anonymous_visits': analytics_data.aggregate(Sum('visitas_anonimas'))['visitas_anonimas__sum'] or 0
        }

        response_data = {
            'trend_data': trend_data,
            'devices_data': devices_data,
            'main_metrics': main_metrics,
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Erro em get_analytics_data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_analytics_admin)
def reset_analytics(request):
    """Reset analytics data."""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Limpa todas as tabelas de analytics
                SiteAnalytics.objects.all().delete()
                PageView.objects.all().delete()
                BookAnalytics.objects.all().delete()
                UserActivityLog.objects.all().delete()

                # Cria registro inicial para hoje
                today = timezone.now().date()
                SiteAnalytics.objects.create(
                    data=today,
                    visitas_total=0,
                    visitas_autenticadas=0,
                    visitas_anonimas=0,
                    usuarios_ativos=0
                )

                # Limpa todos os caches
                try:
                    # Limpa o cache padrão
                    cache.clear()

                    # Se você estiver usando múltiplos caches, pode limpá-los assim:
                    from django.core.cache import caches
                    all_caches = caches.all()
                    for cache_instance in all_caches:
                        cache_instance.clear()

                    logger.info("Cache limpo com sucesso")
                except Exception as cache_error:
                    logger.error(f"Erro ao limpar cache: {str(cache_error)}")
                    # Continue a execução mesmo se houver erro no cache

                return JsonResponse({'success': True})

        except Exception as e:
            logger.error(f"Erro ao resetar analytics: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'Método não permitido'
    }, status=405)


@login_required
@user_passes_test(is_analytics_admin)
def analytics_settings(request):
    """View para configurações do analytics."""
    if request.method == 'POST':
        # TODO: Implementar salvamento das configurações
        pass

    context = {
        'is_analytics_admin': True,
        'page_title': 'Configurações do Analytics'
    }
    return render(request, 'analytics/settings.html', context)


@login_required
@user_passes_test(is_analytics_admin)
def get_devices_data(request):
    """API endpoint para dados de dispositivos."""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        analytics_processor = AnalyticsProcessor()
        devices_data = analytics_processor.process_devices_data(
            PageView.objects.filter(timestamp__date__range=[start_date, end_date])
        )

        return JsonResponse(devices_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_analytics_admin)
def get_books_data(request):
    """API endpoint para dados de livros."""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        books_data = BookAnalytics.objects.filter(
            data__range=[start_date, end_date]
        ).values('livro', 'visualizacoes', 'compartilhamentos_total')

        return JsonResponse({'books_data': list(books_data)})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_analytics_admin)
def get_trend_data(request):
    """API endpoint para dados de tendências."""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        analytics_data = SiteAnalytics.objects.filter(
            data__range=[start_date, end_date]
        )

        trend_data = AnalyticsProcessor.process_trend_data(
            analytics_data, start_date, end_date
        )

        return JsonResponse({'trend_data': trend_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_analytics_admin)
def analytics_settings(request):
    """View para gerenciar configurações do analytics."""
    # Obtém ou cria configurações
    settings = AnalyticsSettings.get_settings()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        try:
            if form_type == 'general':
                # Atualiza configurações gerais
                settings.tracking_enabled = request.POST.get('tracking_enabled') == '1'
                settings.data_retention = int(request.POST.get('data_retention', 90))
                settings.save()

                messages.success(request, 'Configurações gerais atualizadas com sucesso!')

            elif form_type == 'notifications':
                # Atualiza configurações de notificações
                settings.daily_report = request.POST.get('daily_report') == '1'
                settings.alert_threshold = int(request.POST.get('alert_threshold', 100))
                settings.notification_email = request.POST.get('notification_email')
                settings.save()

                messages.success(request, 'Configurações de notificações atualizadas com sucesso!')

            elif form_type == 'cleanup':
                # Executa limpeza de dados
                cleanup_days = int(request.POST.get('cleanup_days', 90))
                cutoff_date = timezone.now() - timedelta(days=cleanup_days)

                # Remove dados antigos
                deleted_counts = {
                    'page_views': PageView.objects.filter(timestamp__lt=cutoff_date).delete()[0],
                    'site_analytics': SiteAnalytics.objects.filter(data__lt=cutoff_date.date()).delete()[0],
                    'book_analytics': BookAnalytics.objects.filter(data__lt=cutoff_date.date()).delete()[0],
                    'search_analytics': SearchAnalytics.objects.filter(timestamp__lt=cutoff_date).delete()[0],
                    'user_activity': UserActivityLog.objects.filter(timestamp__lt=cutoff_date).delete()[0],
                    'error_logs': ErrorLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
                }

                # Atualiza timestamp da última limpeza
                settings.last_cleanup = timezone.now()
                settings.save()

                # Prepara mensagem com contagem de itens removidos
                cleanup_message = 'Limpeza concluída. Registros removidos:\n'
                for key, count in deleted_counts.items():
                    cleanup_message += f'- {key.replace("_", " ").title()}: {count}\n'

                messages.success(request, cleanup_message)

        except ValueError as e:
            messages.error(request, f'Erro ao processar valores: {str(e)}')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar configurações: {str(e)}')

    # Prepara contexto para o template
    context = {
        'settings': settings,
        'last_cleanup_age': None,
        'is_analytics_admin': True
    }

    # Calcula idade da última limpeza
    if settings.last_cleanup:
        cleanup_age = timezone.now() - settings.last_cleanup
        context['last_cleanup_age'] = cleanup_age.days

    return render(request, 'analytics/settings.html', context)


# Função auxiliar para verificar configurações
def check_analytics_settings():
    """Verifica e aplica configurações do analytics."""
    settings = AnalyticsSettings.get_settings()

    if not settings.tracking_enabled:
        return False

    # Verifica se é necessário fazer limpeza automática
    if settings.last_cleanup:
        days_since_cleanup = (timezone.now() - settings.last_cleanup).days
        if days_since_cleanup >= settings.data_retention:
            # Programa limpeza automática
            from django.core.management import call_command
            try:
                call_command('cleanup_analytics')
            except Exception as e:
                print(f"Erro na limpeza automática: {str(e)}")

    return True

# Função para enviar relatório diário
def send_daily_report():
    """Envia relatório diário se configurado."""
    settings = AnalyticsSettings.get_settings()

    if not settings.daily_report or not settings.notification_email:
        return

    try:
        # Gera relatório do dia anterior
        yesterday = timezone.now().date() - timedelta(days=1)
        analytics = SiteAnalytics.objects.filter(data=yesterday).first()

        if not analytics:
            return

        # Prepara dados do relatório
        report_data = {
            'date': yesterday,
            'total_visits': analytics.visitas_total,
            'authenticated_visits': analytics.visitas_autenticadas,
            'anonymous_visits': analytics.visitas_anonimas,
            'active_users': analytics.usuarios_ativos
        }

        # Envia email com relatório
        send_analytics_report_email(
            settings.notification_email,
            report_data
        )

    except Exception as e:
        print(f"Erro ao enviar relatório diário: {str(e)}")


@login_required
@user_passes_test(is_analytics_admin)
def export_excel_report(request):
    """Endpoint para exportação de relatório Excel."""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Obtém dados para exportação
        analytics_processor = AnalyticsProcessor()
        export_data = analytics_processor.get_export_data(start_date, end_date)

        # Cria buffer para o Excel
        output = io.BytesIO()

        # Cria Excel writer
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Analytics Sheet
            analytics_df = pd.DataFrame(export_data['analytics'])
            analytics_df.to_excel(writer, sheet_name='Analytics', index=False)

            # Devices Sheet
            devices_df = pd.DataFrame([
                {'Dispositivo': k, 'Quantidade': v}
                for k, v in export_data['devices'].items()
            ])
            devices_df.to_excel(writer, sheet_name='Dispositivos', index=False)

            # Books Sheet
            books_df = pd.DataFrame(export_data['books'])
            books_df.to_excel(writer, sheet_name='Livros', index=False)

            # Formata as planilhas
            workbook = writer.book
            for sheet in writer.sheets.values():
                sheet.set_column('A:Z', 15)  # Ajusta largura das colunas

        # Prepara resposta
        output.seek(0)
        filename = f'analytics_report_{start_date}_{end_date}.xlsx'

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Erro ao exportar Excel: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_analytics_admin)
def export_csv_report(request):
    """Endpoint para exportação de relatório CSV."""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Obtém dados para exportação
        analytics_processor = AnalyticsProcessor()
        export_data = analytics_processor.get_export_data(start_date, end_date)

        # Cria buffer para CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Escreve cabeçalho
        headers = [
            'Data',
            'Visitas Totais',
            'Visitas Autenticadas',
            'Visitas Anônimas',
            'Usuários Ativos'
        ]
        writer.writerow(headers)

        # Escreve dados
        for record in export_data['analytics']:
            writer.writerow([
                record['data'],
                record.get('visitas_total', 0),
                record.get('visitas_autenticadas', 0),
                record.get('visitas_anonimas', 0),
                record.get('usuarios_ativos', 0)
            ])

        # Prepara resposta
        output.seek(0)
        filename = f'analytics_report_{start_date}_{end_date}.csv'

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_analytics_admin)
def export_pdf_report(request):
    """Endpoint para exportação de relatório PDF."""
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not all([start_date, end_date]):
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Obtém dados para o relatório
        analytics_processor = AnalyticsProcessor()

        analytics_data = SiteAnalytics.objects.filter(
            data__range=[start_date, end_date]
        )

        # Calcula as métricas corretamente usando os nomes dos campos do modelo
        totals = analytics_data.aggregate(
            total_visits=Sum('visitas_total'),
            authenticated_visits=Sum('visitas_autenticadas'),
            anonymous_visits=Sum('visitas_anonimas'),
            active_users=Sum('usuarios_ativos')
        )

        page_views = PageView.objects.filter(
            timestamp__date__range=[start_date, end_date]
        )

        data = {
            'trend_data': AnalyticsProcessor.process_trend_data(
                analytics_data, start_date, end_date
            ),
            'devices_data': analytics_processor.process_devices_data(page_views),
            'main_metrics': {
                'total_visits': totals['total_visits'] or 0,
                'active_users': totals['active_users'] or 0,
                'authenticated_visits': totals['authenticated_visits'] or 0,
                'anonymous_visits': totals['anonymous_visits'] or 0
            }
        }

        # Gera o PDF
        pdf_file = generate_analytics_pdf(
            data,
            start_date.strftime('%d/%m/%Y'),
            end_date.strftime('%d/%m/%Y')
        )

        # Prepara a resposta
        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f'analytics_report_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'error': 'Erro ao gerar relatório PDF',
            'detail': str(e)
        }, status=500)

@login_required
@user_passes_test(is_analytics_admin)
def get_visit_details(request):
    try:
        today = timezone.now().date()
        last_week = today - timedelta(days=7)

        # Busca dados básicos usando select_related para otimizar queries
        visits_data = PageView.objects.filter(
            timestamp__date__range=[last_week, today]
        ).select_related('usuario')

        # Dados para hoje
        today_visits = visits_data.filter(timestamp__date=today).count()

        # Contagem de usuários registrados vs anônimos
        registered_visits = visits_data.filter(usuario__isnull=False).count()
        anonymous_visits = visits_data.filter(usuario__isnull=True).count()

        # Taxa de conversão
        total_visits = registered_visits + anonymous_visits
        conversion_rate = (registered_visits / total_visits * 100) if total_visits > 0 else 0

        # Dados para o gráfico de timeline
        timeline_data = {
            'labels': [],
            'values': []
        }

        for i in range(7):
            date = today - timedelta(days=i)
            count = visits_data.filter(timestamp__date=date).count()
            timeline_data['labels'].append(date.strftime('%d/%m'))
            timeline_data['values'].append(count)

        # Últimas 50 visitas para a tabela, com informações completas
        recent_visits = visits_data.order_by('-timestamp')[:50]

        recent_visits_formatted = []
        for visit in recent_visits:
            visit_data = {
                'timestamp': visit.timestamp.isoformat(),
                'page': visit.url,
                'duration': str(visit.tempo_na_pagina),
                'device': visit.dispositivo,  # Já é um dicionário com type, brand, model, os
                'user': visit.usuario.username if visit.usuario else 'Anônimo'
            }
            recent_visits_formatted.append(visit_data)

        return JsonResponse({
            'todayVisits': today_visits,
            'registeredVisits': registered_visits,
            'anonymousVisits': anonymous_visits,
            'conversionRate': round(conversion_rate, 2),
            'timeline': timeline_data,
            'distribution': {
                'registered': registered_visits,
                'anonymous': anonymous_visits
            },
            'recentVisits': recent_visits_formatted
        })

    except Exception as e:
        logger.error(f"Erro em get_visit_details: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def refresh_session(request):
    if request.user.is_authenticated:
        request.session['last_activity'] = time.time()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'unauthenticated'}, status=401)


@ensure_csrf_cookie
def mark_browser_closing(request):
    if request.method == 'POST' and request.user.is_authenticated:
        request.session['browser_closed'] = True
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
