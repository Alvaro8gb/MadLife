"""
Utility functions for MadLife Event Search Application.

This module contains common utility functions used across the application
for data processing, filtering, and other helper operations.
"""

import pandas as pd
import streamlit as st
from config import SEARCH_CONFIG, UI_MESSAGES


def extract_metadata_options(df):
    """
    Extract unique values for metadata filtering.
    
    Args:
        df (pd.DataFrame): Raw data DataFrame
        
    Returns:
        dict: Dictionary with metadata options for filters
    """
    if df is None or df.empty:
        return {}
    
    metadata_options = {}
    
    # Districts
    districts = df['DISTRITO-INSTALACION'].dropna().unique()
    metadata_options['districts'] = sorted([d for d in districts if d])
    
    # Event types
    types = df['TIPO'].dropna().unique()
    # Clean type names by taking the last part after '/'
    clean_types = []
    for t in types:
        if t and isinstance(t, str):
            clean_type = t.split('/')[-1] if '/' in t else t
            clean_types.append(clean_type)
    metadata_options['types'] = sorted(list(set(clean_types)))
    
    # Free/Paid
    metadata_options['free_options'] = ['Todos', 'Gratuito', 'De pago']
    
    # Venues
    venues = df['NOMBRE-INSTALACION'].dropna().unique()
    metadata_options['venues'] = sorted([v for v in venues if v])[:50]  # Limit to first 50
    
    return metadata_options


def create_metadata_filters(metadata_options):
    """
    Create sidebar filters for metadata.
    
    Args:
        metadata_options (dict): Dictionary with metadata options
        
    Returns:
        dict: Dictionary with selected filter values
    """
    st.sidebar.markdown("### 🔍 Filtros de Búsqueda")
    
    filters = {}
    
    # District filter
    if 'districts' in metadata_options and metadata_options['districts']:
        selected_district = st.sidebar.selectbox(
            "Distrito:",
            ['Todos'] + metadata_options['districts'],
            index=0
        )
        if selected_district != 'Todos':
            filters['district'] = selected_district
    
    # Event type filter
    if 'types' in metadata_options and metadata_options['types']:
        selected_type = st.sidebar.selectbox(
            "Tipo de Evento:",
            ['Todos'] + metadata_options['types'],
            index=0
        )
        if selected_type != 'Todos':
            filters['type'] = selected_type
    
    # Free/Paid filter
    free_option = st.sidebar.selectbox(
        "Precio:",
        metadata_options.get('free_options', ['Todos']),
        index=0
    )
    if free_option == 'Gratuito':
        filters['free'] = '1'
    elif free_option == 'De pago':
        filters['free'] = '0'
    
    # Venue filter
    if 'venues' in metadata_options and metadata_options['venues']:
        selected_venue = st.sidebar.selectbox(
            "Lugar:",
            ['Todos'] + metadata_options['venues'],
            index=0
        )
        if selected_venue != 'Todos':
            filters['venue'] = selected_venue
    
    return filters


def apply_filters_to_results(results_df, filters):
    """
    Apply metadata filters to search results.
    
    Args:
        results_df (pd.DataFrame): DataFrame with search results
        filters (dict): Dictionary with filter criteria
        
    Returns:
        pd.DataFrame: Filtered results DataFrame
    """
    if filters and not results_df.empty:
        for key, value in filters.items():
            if key == 'district':
                results_df = results_df[results_df['district'].str.contains(value, case=False, na=False)]
            elif key == 'type':
                results_df = results_df[results_df['type'].str.contains(value, case=False, na=False)]
            elif key == 'free':
                results_df = results_df[results_df['free'] == value]
            elif key == 'venue':
                results_df = results_df[results_df['venue'].str.contains(value, case=False, na=False)]
    
    return results_df


def apply_date_filter(results_df, date_since, date_to):
    """
    Apply date range filter to search results.
    
    Args:
        results_df (pd.DataFrame): DataFrame with search results
        date_since (datetime): Start date for filtering
        date_to (datetime): End date for filtering
        
    Returns:
        pd.DataFrame: Filtered results DataFrame
    """
    dts = pd.to_datetime(date_since)
    dto = pd.to_datetime(date_to)
    results_df['date'] = pd.to_datetime(results_df['date'], errors='coerce')
    filtered_df = results_df[(results_df['date'] >= dts) & (results_df['date'] <= dto)]
    return filtered_df


def get_date_range_from_data(df):
    """
    Extract min and max dates from the data for date range filter.
    
    Args:
        df (pd.DataFrame): Raw data DataFrame
        
    Returns:
        tuple: (min_date, max_date)
    """
    try:
        date_series = pd.to_datetime(df['FECHA'], errors='coerce')
        min_date = date_series.min().date() if not date_series.isna().all() else pd.to_datetime('today').date()
        max_date = date_series.max().date() if not date_series.isna().all() else pd.to_datetime('today').date()
    except Exception:
        min_date = pd.to_datetime('today').date()
        max_date = pd.to_datetime('today').date()
    
    return min_date, max_date


def create_search_configuration_sidebar():
    """
    Create search configuration controls in sidebar.
    
    Returns:
        dict: Dictionary with search configuration
    """
    st.sidebar.markdown("### ⚙️ Configuración de Búsqueda")
    
    n_results = st.sidebar.slider(
        "Número de resultados:", 
        min_value=SEARCH_CONFIG['min_results'], 
        max_value=SEARCH_CONFIG['max_results'], 
        value=SEARCH_CONFIG['default_results']
    )
    
    show_analytics = st.sidebar.checkbox("Mostrar dashboard de análisis", value=False)
    
    return {
        'n_results': n_results,
        'show_analytics': show_analytics
    }


def prepare_export_data(results_df):
    """
    Prepare results data for CSV export.
    
    Args:
        results_df (pd.DataFrame): DataFrame with search results
        
    Returns:
        str: CSV data as string
    """
    if results_df.empty:
        return ""
    
    export_df = results_df[['rank', 'title', 'similarity_score', 'date', 'time', 
                           'district', 'venue', 'type', 'free', 'url']].copy()
    export_df.columns = ['Ranking', 'Título', 'Similitud', 'Fecha', 'Hora',
                       'Distrito', 'Lugar', 'Tipo', 'Gratuito', 'URL']
    
    return export_df.to_csv(index=False, encoding='utf-8')


def initialize_session_state():
    """Initialize session state variables."""
    if 'selected_event' not in st.session_state:
        st.session_state.selected_event = None
    
    if 'suggested_query' not in st.session_state:
        st.session_state.suggested_query = None


def handle_suggested_query():
    """Handle suggested query from no results screen."""
    if st.session_state.get('suggested_query'):
        query = st.session_state.suggested_query
        st.session_state.suggested_query = None
        return query
    return None


def display_example_queries():
    """Display example query buttons."""
    from config import EXAMPLE_QUERIES
    
    st.markdown("**💡 Ejemplos de búsquedas:**")
    
    cols = st.columns(3)
    for i, example in enumerate(EXAMPLE_QUERIES):
        with cols[i % 3]:
            if st.button(f"🔎 {example}", key=f"example_{i}"):
                return example
    
    return None


def show_loading_message():
    """Show loading message during search."""
    return st.spinner(UI_MESSAGES['loading'])


def normalize_date_range(date_range):
    """
    Normalize date range input to ensure two values.
    
    Args:
        date_range: Date range from date_input widget
        
    Returns:
        tuple: (date_since, date_to)
    """
    if len(date_range) == 2:
        return date_range[0], date_range[1]
    else:
        return date_range[0], date_range[0]
