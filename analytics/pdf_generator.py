# analytics/pdf_generator.py

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Gerador de relatórios PDF para analytics com suporte a múltiplas seções,
    gráficos e formatação avançada.
    """

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados para o relatório."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10
        ))

        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.white
        ))

    def _create_header(self, elements):
        """Cria o cabeçalho do relatório."""
        title = Paragraph(
            f"Relatório de Analytics<br/>Período: {self.start_date} a {self.end_date}",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))

        generation_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        date_line = Paragraph(
            f"Gerado em: {generation_time}",
            self.styles['Normal']
        )
        elements.append(date_line)
        elements.append(Spacer(1, 30))

    def _create_summary_section(self, elements, data):
        """Cria seção de resumo com métricas principais."""
        header = Paragraph("Resumo do Período", self.styles['SectionHeader'])
        elements.append(header)

        summary_data = [
            ['Métrica', 'Total'],
            ['Visitas Totais', str(data.get('total_visits', 0))],
            ['Usuários Ativos', str(data.get('active_users', 0))],
            ['Visitas Autenticadas', str(data.get('authenticated_visits', 0))],
            ['Visitas Anônimas', str(data.get('anonymous_visits', 0))]
        ]

        table = Table(summary_data, colWidths=[4 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT')
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

    def _create_trend_section(self, elements, trend_data):
        """Cria seção com dados de tendência."""
        if not trend_data:
            return

        header = Paragraph("Tendência de Visitas", self.styles['SectionHeader'])
        elements.append(header)

        table_data = [['Data', 'Total', 'Autenticadas', 'Anônimas']]

        for day in trend_data:
            table_data.append([
                day['date'],
                str(day.get('total', 0)),
                str(day.get('authenticated', 0)),
                str(day.get('anonymous', 0))
            ])

        table = Table(table_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT')
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

    def _create_devices_section(self, elements, devices_data):
        """Cria seção com dados de dispositivos."""
        if not devices_data:
            return

        header = Paragraph("Distribuição por Dispositivos", self.styles['SectionHeader'])
        elements.append(header)

        table_data = [['Tipo de Dispositivo', 'Quantidade', 'Porcentagem']]
        total_devices = sum(devices_data.values())

        for device, count in devices_data.items():
            percentage = (count / total_devices * 100) if total_devices > 0 else 0
            table_data.append([
                device.capitalize(),
                str(count),
                f"{percentage:.1f}%"
            ])

        table = Table(table_data, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT')
        ]))

        elements.append(table)

    def generate_report(self, data):
        """
        Gera o relatório PDF completo.

        Args:
            data: Dicionário com todos os dados necessários para o relatório

        Returns:
            BytesIO: Buffer contendo o PDF gerado
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),
                rightMargin=inch / 2,
                leftMargin=inch / 2,
                topMargin=inch / 2,
                bottomMargin=inch / 2
            )

            elements = []

            self._create_header(elements)

            if 'main_metrics' in data:
                self._create_summary_section(elements, data['main_metrics'])

            if 'trend_data' in data:
                self._create_trend_section(elements, data['trend_data'])

            if 'devices_data' in data:
                self._create_devices_section(elements, data['devices_data'])

            doc.build(elements)
            buffer.seek(0)
            return buffer

        except Exception as e:
            logger.error(f"Erro ao gerar relatório PDF: {str(e)}", exc_info=True)
            raise


def generate_analytics_pdf(data, start_date, end_date):
    """Função auxiliar para gerar o relatório PDF de analytics."""
    generator = PDFReportGenerator(start_date, end_date)
    return generator.generate_report(data)