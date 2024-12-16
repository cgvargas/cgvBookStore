from django.utils import timezone
from django.db.models import F
from django.core.cache import cache
from datetime import timedelta, datetime
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import io

from django.utils.crypto import get_random_string
import logging
from .models import SiteAnalytics, PageView, BookAnalytics
from functools import lru_cache
import json

from .pdf_generator import generate_analytics_pdf

logger = logging.getLogger(__name__)


class AnalyticsValidationError(Exception):
    """Custom exception for analytics validation errors."""
    pass


class AnalyticsProcessor:
    """
    Processes and analyzes site analytics data with caching and validation.
    """
    CACHE_TIMEOUT = 300  # 5 minutes cache

    def __init__(self):
        self.today = timezone.now().date()
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def validate_date_range(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> tuple:
        """
        Validates and normalizes date range parameters.

        Args:
            start_date: Start date (string 'YYYY-MM-DD' or datetime object)
            end_date: End date (string 'YYYY-MM-DD' or datetime object)

        Returns:
            tuple: Normalized (start_date, end_date) as datetime.date objects

        Raises:
            AnalyticsValidationError: If dates are invalid or range is too large
        """
        try:
            # Convert string dates to datetime objects if necessary
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Convert datetime to date if necessary
            if isinstance(start_date, datetime):
                start_date = start_date.date()
            if isinstance(end_date, datetime):
                end_date = end_date.date()

            # Validate date range
            if start_date > end_date:
                raise AnalyticsValidationError("Start date must be before end date")

            # Limit date range to 1 year
            if (end_date - start_date).days > 365:
                raise AnalyticsValidationError("Date range cannot exceed 1 year")

            return start_date, end_date

        except ValueError as e:
            raise AnalyticsValidationError(f"Invalid date format: {str(e)}")
        except Exception as e:
            raise AnalyticsValidationError(f"Error validating dates: {str(e)}")

    @staticmethod
    @lru_cache(maxsize=100)
    def process_trend_data(queryset, start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
        """
        Processes trend data with caching and validation.

        Args:
            queryset: Django queryset with analytics data
            start_date: Start date
            end_date: End date

        Returns:
            List of dictionaries with daily analytics data
        """
        cache_key = f'trend_data_{start_date}_{end_date}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        try:
            data_dict = {
                record.data: {
                    'total': record.visitas_total,
                    'authenticated': record.visitas_autenticadas,
                    'anonymous': record.visitas_anonimas,
                    'active_users': record.usuarios_ativos
                } for record in queryset
            }

            trend_data = []
            current_date = start_date

            while current_date <= end_date:
                daily_data = data_dict.get(current_date, {
                    'total': 0,
                    'authenticated': 0,
                    'anonymous': 0,
                    'active_users': 0
                })

                trend_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    **daily_data
                })

                current_date += timedelta(days=1)

            # Cache the results
            cache.set(cache_key, json.dumps(trend_data), AnalyticsProcessor.CACHE_TIMEOUT)
            return trend_data

        except Exception as e:
            logger.error(f"Error processing trend data: {str(e)}", exc_info=True)
            return []

    def process_devices_data(self, page_views) -> Dict[str, int]:
        """
        Processes device data with enhanced aggregation and caching.

        Args:
            page_views: QuerySet of PageView objects

        Returns:
            Dictionary with device counts
        """
        cache_key = f'devices_data_{self.today}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        try:
            device_counts = {}

            # Optimize query with select_related if needed
            unique_sessions = page_views.filter(
                timestamp__date=self.today
            ).values('sessao_id').distinct()

            for session in unique_sessions:
                visit = page_views.filter(
                    sessao_id=session['sessao_id']
                ).values('dispositivo').first()

                if visit and visit['dispositivo']:
                    try:
                        device_info = (
                            visit['dispositivo']
                            if isinstance(visit['dispositivo'], dict)
                            else json.loads(visit['dispositivo'])
                        )
                        device_type = device_info.get('type', 'unknown')
                        device_counts[device_type] = device_counts.get(device_type, 0) + 1
                    except (json.JSONDecodeError, AttributeError, KeyError) as e:
                        self.logger.warning(f"Error processing device info: {str(e)}")
                        continue

            # Cache the results
            cache.set(cache_key, json.dumps(device_counts), AnalyticsProcessor.CACHE_TIMEOUT)
            return device_counts

        except Exception as e:
            self.logger.error(f"Error processing device data: {str(e)}", exc_info=True)
            return {'unknown': 0}

    @staticmethod
    def calculate_growth_rates(current_data: Dict, previous_data: Dict) -> Dict[str, float]:
        """
        Calculates growth rates between two periods with validation.

        Args:
            current_data: Current period metrics
            previous_data: Previous period metrics

        Returns:
            Dictionary with growth rates
        """
        try:
            growth_rates = {}
            metrics = ['visitas_total', 'visitas_autenticadas', 'visitas_anonimas', 'usuarios_ativos']

            for metric in metrics:
                current = float(current_data.get(metric, 0))
                previous = float(previous_data.get(metric, 0))

                if previous > 0:
                    growth = ((current - previous) / previous) * 100
                    growth_rates[f'{metric}_growth'] = round(growth, 1)
                else:
                    growth_rates[f'{metric}_growth'] = 100.0 if current > 0 else 0.0

            return growth_rates

        except (TypeError, ValueError) as e:
            logger.error(f"Error calculating growth rates: {str(e)}")
            return {f'{metric}_growth': 0.0 for metric in metrics}

    @staticmethod
    def generate_excel_report(data: Dict, start_date: datetime.date, end_date: datetime.date) -> io.BytesIO:
        """
        Generates Excel report with error handling and validation.

        Args:
            data: Analytics data dictionary
            start_date: Start date
            end_date: End date

        Returns:
            BytesIO object containing Excel file
        """
        try:
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D9EAD3',
                    'border': 1
                })

                # Trend data sheet
                if 'trend_data' in data and data['trend_data']:
                    visits_df = pd.DataFrame(data['trend_data'])
                    visits_df.to_excel(writer, sheet_name='Visitas', index=False)
                    worksheet = writer.sheets['Visitas']

                    for idx, col in enumerate(visits_df.columns):
                        worksheet.write(0, idx, col, header_format)
                        worksheet.set_column(idx, idx, 15)

                # Devices data sheet
                if 'devices_data' in data and data['devices_data']:
                    devices_df = pd.DataFrame(
                        list(data['devices_data'].items()),
                        columns=['Device', 'Total']
                    )
                    devices_df.to_excel(writer, sheet_name='Dispositivos', index=False)
                    worksheet = writer.sheets['Dispositivos']

                    for idx, col in enumerate(devices_df.columns):
                        worksheet.write(0, idx, col, header_format)
                        worksheet.set_column(idx, idx, 15)

                # Books data sheet
                if 'books_data' in data and data['books_data']:
                    books_df = pd.DataFrame(data['books_data'])
                    books_df.to_excel(writer, sheet_name='Livros', index=False)
                    worksheet = writer.sheets['Livros']

                    for idx, col in enumerate(books_df.columns):
                        worksheet.write(0, idx, col, header_format)
                        worksheet.set_column(idx, idx, 15)

            output.seek(0)
            return output

        except Exception as e:
            logger.error(f"Error generating Excel report: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def generate_pdf_report(data: Dict, start_date: datetime.date, end_date: datetime.date) -> io.BytesIO:
        """
        Gera relatório em PDF usando o PDFReportGenerator.

        Args:
            data: Dados do analytics
            start_date: Data inicial
            end_date: Data final

        Returns:
            BytesIO: Buffer contendo o PDF gerado
        """
        try:
            return generate_analytics_pdf(
                data,
                start_date.strftime('%d/%m/%Y'),
                end_date.strftime('%d/%m/%Y')
            )
        except Exception as e:
            logger.error(f"Erro ao gerar relatório PDF: {str(e)}", exc_info=True)
            raise

    # Adicione este método à sua classe AnalyticsProcessor

    @staticmethod
    def get_export_data(start_date: datetime.date, end_date: datetime.date) -> Dict[str, Any]:
        """
        Obtém dados consolidados para exportação em diferentes formatos.

        Args:
            start_date: Data inicial do período
            end_date: Data final do período

        Returns:
            Dictionary com dados consolidados para exportação

        Raises:
            AnalyticsValidationError: Se as datas forem inválidas
            Exception: Para outros erros durante o processamento
        """
        try:
            # Valida o intervalo de datas
            start_date, end_date = AnalyticsProcessor.validate_date_range(start_date, end_date)

            # Busca dados do período
            analytics_data = SiteAnalytics.objects.filter(
                data__range=[start_date, end_date]
            ).order_by('data')

            page_views = PageView.objects.filter(
                timestamp__date__range=[start_date, end_date]
            )

            books_data = BookAnalytics.objects.filter(
                data__range=[start_date, end_date]
            )

            # Cache key para resultados
            cache_key = f'export_data_{start_date}_{end_date}'
            cached_data = cache.get(cache_key)

            if cached_data:
                return json.loads(cached_data)

            export_data = {
                'analytics': [],
                'devices': {},
                'books': [],
                'summary': {
                    'period_start': start_date.strftime('%Y-%m-%d'),
                    'period_end': end_date.strftime('%Y-%m-%d'),
                    'total_visits': 0,
                    'total_users': 0,
                    'total_views': 0
                }
            }

            # Processa dados de analytics
            for record in analytics_data:
                export_data['analytics'].append({
                    'data': record.data.strftime('%Y-%m-%d'),
                    'visitas_total': record.visitas_total,
                    'visitas_autenticadas': record.visitas_autenticadas,
                    'visitas_anonimas': record.visitas_anonimas,
                    'usuarios_ativos': record.usuarios_ativos
                })
                export_data['summary']['total_visits'] += record.visitas_total
                export_data['summary']['total_users'] += record.usuarios_ativos

            # Processa dados de dispositivos
            for view in page_views:
                try:
                    device_info = (
                        json.loads(view.dispositivo)
                        if isinstance(view.dispositivo, str)
                        else view.dispositivo
                    )
                    device_type = device_info.get('type', 'unknown')
                    export_data['devices'][device_type] = (
                            export_data['devices'].get(device_type, 0) + 1
                    )
                except (json.JSONDecodeError, AttributeError, KeyError):
                    export_data['devices']['unknown'] = (
                            export_data['devices'].get('unknown', 0) + 1
                    )

            # Processa dados de livros
            for book in books_data:
                export_data['books'].append({
                    'data': book.data.strftime('%Y-%m-%d'),
                    'livro': book.livro,
                    'visualizacoes': book.visualizacoes,
                    'compartilhamentos_total': (
                            book.compartilhamentos_facebook +
                            book.compartilhamentos_twitter +
                            book.compartilhamentos_whatsapp
                    ),
                    'adicoes_estante': book.adicoes_estante
                })
                export_data['summary']['total_views'] += book.visualizacoes

            # Cache os resultados
            cache.set(cache_key, json.dumps(export_data), AnalyticsProcessor.CACHE_TIMEOUT)

            return export_data

        except AnalyticsValidationError as e:
            logger.error(f"Erro de validação ao exportar dados: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao processar dados para exportação: {str(e)}", exc_info=True)
            raise


def safe_cache_key(key: str) -> str:
    """
    Gera uma chave de cache segura removendo caracteres problemáticos.

    Args:
        key: A chave original que pode conter caracteres especiais

    Returns:
        str: Uma chave segura para uso com qualquer backend de cache
    """
    return ''.join(c for c in key if c.isalnum() or c in '-_') + '_' + get_random_string(8)


def register_book_view(book_title: str, user=None) -> bool:
    """
    Registra a visualização de um livro com validação e tratamento de erros.

    Args:
        book_title: Título do livro
        user: Objeto usuário opcional

    Returns:
        bool: Indica sucesso ou falha no registro
    """
    if not book_title:
        logger.error("Book title cannot be empty")
        return False

    try:
        today = timezone.now().date()
        user_id = user.id if user and user.is_authenticated else 'anonymous'

        # Gera uma chave segura para o cache
        base_key = f'book_view_{book_title}_{today}_{user_id}'
        cache_key = safe_cache_key(base_key)

        # Verifica se já existe no cache para prevenir contagens duplicadas
        if cache.get(cache_key):
            return True

        # Registra ou atualiza a visualização no banco de dados
        analytics, created = BookAnalytics.objects.get_or_create(
            livro=book_title,
            data=today,
            defaults={
                'visualizacoes': 1,
                'compartilhamentos_facebook': 0,
                'compartilhamentos_twitter': 0,
                'compartilhamentos_whatsapp': 0,
                'adicoes_estante': 0
            }
        )

        if not created:
            analytics.visualizacoes = F('visualizacoes') + 1
            analytics.save()

        # Armazena no cache por 5 minutos para prevenir duplicatas
        cache.set(cache_key, True, 300)  # 5 minutos

        logger.info(f"Book view registered: {book_title} by user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error registering book view for {book_title}: {str(e)}", exc_info=True)
        return False

    except Exception as e:
        logger.error(f"Error registering book view for {book_title}: {str(e)}", exc_info=True)
        return False