# -- coding: utf-8 --
"""
Модуль для экспорта данных в PDF.
Использует ReportLab для генерации PDF с поддержкой русского языка.
"""
import os
from pathlib import Path
from typing import List
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# Предполагается, что класс PhoneRecord импортирован корректно
from database import PhoneRecord


class PDFExporter:
    """Экспортёр данных в PDF."""

    # Пути поиска шрифта DejaVuSans (исправлены пути)
    FONT_SEARCH_PATHS = [
        Path(__file__).parent / "fonts" / "DejaVuSans.ttf",
        Path(__file__).parent / "DejaVuSans.ttf",
        Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts" / "DejaVuSans.ttf",
        Path("C:/Windows/Fonts/DejaVuSans.ttf"),
        Path.home() / ".fonts" / "DejaVuSans.ttf",
    ]

    def __init__(self):
        """Инициализация экспортёра."""
        self.font_registered = False
        self.font_name = "DejaVuSans"
        self._register_font()

    def _register_font(self):
        """Регистрирует шрифт для поддержки русского языка."""
        for font_path in self.FONT_SEARCH_PATHS:
            if font_path.exists():
                try:
                    pdfmetrics.registerFont(TTFont(self.font_name, str(font_path)))
                    self.font_registered = True
                    return
                except Exception:
                    continue

        # Если DejaVuSans не найден, попробуем системные шрифты
        try:
            arial_path = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts" / "arial.ttf"
            if arial_path.exists():
                pdfmetrics.registerFont(TTFont("Arial", str(arial_path)))
                self.font_name = "Arial"
                self.font_registered = True
                return
        except Exception:
            pass

        # Используем стандартный шрифт (без русского)
        self.font_name = "Helvetica"
        self.font_registered = False

    def get_font_status(self) -> tuple[bool, str]:
        """
        Возвращает статус шрифта.

        Returns:
            Кортеж (шрифт зарегистрирован, название шрифта).
        """
        return self.font_registered, self.font_name

    def _calculate_column_widths(self, records: List[PhoneRecord], available_width: float) -> List[float]:
        """
        Рассчитывает ширину столбцов автоматически с приоритетом для ФИО.

        Args:
            records: Список записей.
            available_width: Доступная ширина страницы в points/mm.

        Returns:
            Список ширины для каждого столбца.
        """
        # Заголовки столбцов
        headers = ["№", "ФИО", "Номер", "Login", "Password", "IP-адрес", "Локация", "Комментарий"]

        # 1. Вычисляем максимальную длину текста для каждого столбца
        # Индексы: 0-№, 1-ФИО, 2-Номер, 3-Login, 4-Password, 5-IP, 6-Локация, 7-Коммент
        max_lengths = [len(h) for h in headers]

        # Учитываем длину данных в записях
        for record in records:
            data = [
                str(len(records)),  # Примерная длина номера строки
                record.full_name,
                record.phone_number,
                record.login,
                record.password,
                record.ip_address,
                record.location,
                record.comment
            ]
            for i, val in enumerate(data):
                if i < len(max_lengths):
                    max_lengths[i] = max(max_lengths[i], len(str(val)))

        # 2. Задаем весовые коэффициенты (приоритеты)
        # ФИО (индекс 1) получает вес 3.0, остальные меньше
        weights = [1.0, 3.0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5]

        # 3. Считаем "весовую длину" для каждого столбца
        weighted_lengths = [max_lengths[i] * weights[i] for i in range(len(headers))]

        total_weighted = sum(weighted_lengths)

        if total_weighted == 0:
            # Если данных нет, распределяем равномерно
            return [available_width / len(headers)] * len(headers)

        # 4. Нормализуем под доступную ширину страницы
        factor = available_width / total_weighted
        col_widths = [w * factor for w in weighted_lengths]

        # 5. Гарантируем минимальную ширину для важных колонок (опционально)
        # Например, ФИО не должно быть меньше 40mm
        min_fio_width = 40 * mm
        if col_widths[1] < min_fio_width:
            # Если ФИО слишком узкое, добавляем разницу, пропорционально уменьшая остальные
            deficit = min_fio_width - col_widths[1]
            # Уменьшаем остальные колонки (кроме ФИО и №)
            adjustable_indices = [2, 3, 4, 5, 6, 7]
            adjustable_total = sum(col_widths[i] for i in adjustable_indices)

            if adjustable_total > deficit:
                col_widths[1] = min_fio_width
                ratio = (adjustable_total - deficit) / adjustable_total
                for i in adjustable_indices:
                    col_widths[i] *= ratio
            else:
                # Если места критически мало, все равно ставим минимум ФИО
                col_widths[1] = min_fio_width

        return col_widths

    def export_to_pdf(self, output_path: Path, records: List[PhoneRecord],
                      notes_text: str = " ") -> tuple[bool, str]:
        """
        Экспортирует данные в PDF-файл.

        Args:
            output_path: Путь к выходному файлу.
            records: Список записей для экспорта.
            notes_text: Текст заметок.

        Returns:
            Кортеж (успех, сообщение).
        """
        try:
            # Создаем документ, чтобы узнать доступную ширину
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=landscape(A4),
                rightMargin=1 * cm,
                leftMargin=1 * cm,
                topMargin=1 * cm,
                bottomMargin=1 * cm
            )

            # Вычисляем доступную ширину для таблицы
            available_width = doc.pagesize[0] - doc.leftMargin - doc.rightMargin

            elements = []
            styles = getSampleStyleSheet()

            # Создаём стили с русским шрифтом
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=18,
                alignment=1,  # По центру
                spaceAfter=20
            )

            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                alignment=1,
                textColor=colors.gray,
                spaceAfter=20
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10
            )

            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10
            )

            # Заголовок
            elements.append(Paragraph("АЛТАЙЦИНК - База IP-телефонов", title_style))

            # Дата и время
            date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
            elements.append(Paragraph(f"Экспорт от {date_str} | Записей: {len(records)}", subtitle_style))

            if records:
                # Заголовок таблицы
                elements.append(Paragraph("Таблица телефонов", heading_style))

                # Создаём таблицу
                table_data = [
                    ["№", "ФИО", "Номер", "Login", "Password", "IP-адрес", "Локация", "Комментарий"]
                ]

                for i, record in enumerate(records, 1):
                    table_data.append([
                        str(i),
                        record.full_name,
                        record.phone_number,
                        record.login,
                        record.password,
                        record.ip_address,
                        record.location,
                        record.comment[:30] + "..." if len(record.comment) > 30 else record.comment
                    ])

                # АВТОМАТИЧЕСКИЙ РАСЧЕТ ШИРИНЫ
                col_widths = self._calculate_column_widths(records, available_width)

                table = Table(table_data, colWidths=col_widths, repeatRows=1)

                table.setStyle(TableStyle([
                    # Заголовок
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTNAME', (0, 1), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                    # Границы
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),

                    # Чередование цветов строк
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),

                    # Отступы
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ]))

                elements.append(table)
            else:
                elements.append(Paragraph("База данных пуста.", normal_style))

            # Добавляем заметки, если есть
            if notes_text and notes_text.strip():
                elements.append(Spacer(1, 30))
                elements.append(Paragraph("Дополнительная информация", heading_style))

                # Разбиваем текст на параграфы
                for line in notes_text.strip().split('\n'):
                    if line.strip():
                        elements.append(Paragraph(line, normal_style))
                    else:
                        elements.append(Spacer(1, 6))

            # Генерируем PDF
            doc.build(elements)

            return True, f"PDF успешно сохранён: {output_path}"

        except Exception as e:
            return False, f"Ошибка при создании PDF: {str(e)}"