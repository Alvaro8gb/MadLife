"""
Visualizations package for MadLife Event Search Application.

This package contains different visualization components for the application:
- event_detail: Detailed event view with calendar export functionality
- search_results: Search results display with interactive elements
- charts: Various charts and analytics visualizations
- calendar_export: Calendar export utilities and functions
"""

from .events import display_event_detail
from .search_results import display_search_results, display_search_summary
from .charts import create_similarity_chart, render_analytics_dashboard
from .calendar_export import create_calendar_export_links, generate_ics_content

