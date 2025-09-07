"""
Configuration and utilities for MadLife Event Search Application.

This module contains configuration constants, utility functions, and
common configurations used across the application.
"""

# Application configuration
APP_CONFIG = {
    'page_title': 'MadLife',
    'page_icon': '🎭',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Search configuration
SEARCH_CONFIG = {
    'default_results': 10,
    'max_results': 50,
    'min_results': 5,
    'default_description_length': 200
}

# Calendar export configuration
CALENDAR_CONFIG = {
    'default_duration_hours': 2,
    'timezone': 'Europe/Madrid',
    'uid_domain': 'madlife.com'
}

# UI Messages
UI_MESSAGES = {
    'no_results': "🔍 No se encontraron eventos similares para la búsqueda.",
    'loading': "🔍 Buscando eventos similares...",
    'db_loaded': "✅ Base de datos de embeddings cargada correctamente!",
    'db_created': "✅ Base de datos creada exitosamente!",
    'db_error': "❌ Fallo al crear la base de datos"
}

# Example queries for the interface
EXAMPLE_QUERIES = [
    "concierto música clásica",
    "teatro infantil familiar",
    "exposición arte contemporáneo",
    "taller de cocina",
    "actividades deportivas",
    "festival flamenco"
]

# Color schemes for charts
COLOR_SCHEMES = {
    'similarity': 'viridis',
    'free_events': '#28a745',
    'paid_events': '#ffc107',
    'google_calendar': '#4285f4',
    'outlook_calendar': '#0078d4',
    'yahoo_calendar': '#7b0099'
}

# Date formats
DATE_FORMATS = {
    'display': '%A, %d de %B de %Y',
    'short': '%d/%m/%Y',
    'calendar_export': '%Y%m%dT%H%M%S',
    'ics': '%Y%m%dT%H%M%SZ'
}

# Field mappings for data processing
FIELD_MAPPINGS = {
    'csv_to_display': {
        'TITULO': 'title',
        'DESCRIPCION': 'description_preview',
        'FECHA': 'date',
        'HORA': 'time',
        'DISTRITO-INSTALACION': 'district',
        'NOMBRE-INSTALACION': 'venue',
        'TIPO': 'type',
        'GRATUITO': 'free',
        'CONTENT-URL': 'url'
    }
}


def get_month_name_spanish(month_num):
    """Get Spanish month name from month number."""
    months = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    return months.get(month_num, '')


def get_weekday_name_spanish(weekday_num):
    """Get Spanish weekday name from weekday number."""
    weekdays = {
        0: 'lunes', 1: 'martes', 2: 'miércoles', 3: 'jueves',
        4: 'viernes', 5: 'sábado', 6: 'domingo'
    }
    return weekdays.get(weekday_num, '')
