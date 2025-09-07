"""
Search page for MadLife Event Search Application.
"""

import os
import time
import streamlit as st
import pandas as pd

# Import application modules
from config import UI_MESSAGES
from utils import (
    extract_metadata_options, 
    create_metadata_filters,
    apply_filters_to_results,
    apply_date_filter,
    get_date_range_from_data,
    create_search_configuration_sidebar,
    prepare_export_data,
    initialize_session_state,
    handle_suggested_query,
    display_example_queries,
    show_loading_message,
    normalize_date_range
)

from core import (
    display_search_results,
    display_search_summary,
    render_analytics_dashboard
)

from embedding_db import EventEmbeddingManager, create_embedding_database
from apiManager import load_madrid_events_data


@st.cache_resource
def initialize_embedding_manager(df: pd.DataFrame):
    """Initialize the embedding manager with caching for better performance."""
    db_path = "./chroma_db"
    
    # Check if database exists
    if os.path.exists(db_path) and os.listdir(db_path):
        # Load existing database
        manager = EventEmbeddingManager(db_path=db_path)
        # Show success message briefly
        _placeholder = st.empty()
        _placeholder.success(UI_MESSAGES['db_loaded'])
        time.sleep(2)
        _placeholder.empty()
    elif len(df) > 0:
        with st.spinner("Creando base de datos por primera vez..."):
            manager = create_embedding_database(df, db_path)
        
        # Show creation success message briefly
        _placeholder = st.empty()
        _placeholder.success(UI_MESSAGES['db_created'])
        time.sleep(3)
        _placeholder.empty()
    else:
        st.error(UI_MESSAGES['db_error'])
        return None
    
    return manager


def show_search_page():
    """Display the main search page."""
    
    # Initialize session state
    initialize_session_state()
    
    # Check for suggested queries
    suggested_query = handle_suggested_query()
    
    # Header
    st.title("🎭 MadLife Buscador de Eventos")
    st.markdown("Busca el evento que mejor se adapte a ti")

    # Load raw data for metadata
    raw_df = load_madrid_events_data()
    metadata_options = extract_metadata_options(raw_df)
    
    # Initialize embedding manager
    manager = initialize_embedding_manager(raw_df)
    
    if manager is None:
        st.stop()
    
    # Database stats
    stats = manager.get_collection_stats()
    st.sidebar.metric("Número de Eventos", stats['total_events'])
    
    # Create metadata filters
    filters = create_metadata_filters(metadata_options)
    
    # Date range filter
    min_date, max_date = get_date_range_from_data(raw_df)
    
    st.sidebar.markdown("### 📅 Filtrar por fecha (fecha de inicio)")
    date_range = st.sidebar.date_input(
        "Intervalo de fechas:",
        value=(min_date, max_date),
        format="DD/MM/YYYY",
    )
    
    date_since, date_to = normalize_date_range(date_range)
    
    # Search configuration
    search_config = create_search_configuration_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Use suggested query if available
        query_input = suggested_query if suggested_query else ""
        
        query = st.text_input(
            "🔍 **Buscar eventos:**",
            value=query_input,
            placeholder="Ej: concierto música clásica, teatro infantil, exposición arte moderno...",
            help="Describe el tipo de evento que buscas en lenguaje natural"
        )
        
        # Example queries
        example_query = display_example_queries()
        if example_query:
            query = example_query
        
        # Search execution
        if query:
            with show_loading_message():
                # Search for similar events
                results_df = manager.export_similar_events_df(
                    query=query,
                    n_results=search_config['n_results']
                )
                
                # Apply filters
                if filters and not results_df.empty:
                    results_df = apply_filters_to_results(results_df, filters)
                
                # Apply date filter
                results_df = apply_date_filter(results_df, date_since, date_to)
                
                # Reset index after filtering
                results_df.reset_index(drop=True, inplace=True)
                results_df['rank'] = range(1, len(results_df) + 1)
        else:
            results_df = pd.DataFrame()  # Initialize empty DataFrame when no query
            
        # Display results
        if query:
            display_search_results(results_df, query)
    
    with col2:
        if query and 'results_df' in locals() and not results_df.empty:
            display_search_summary(results_df)
    
    # Analytics dashboard
    if query and 'results_df' in locals() and search_config['show_analytics'] and not results_df.empty:
        st.markdown("---")
        render_analytics_dashboard(results_df)
    
    # Export functionality
    if query and 'results_df' in locals() and not results_df.empty:
        st.markdown("### 💾 Exportar Resultados")
        
        csv_data = prepare_export_data(results_df)
        
        st.download_button(
            label="📥 Descargar resultados (CSV)",
            data=csv_data,
            file_name=f"eventos_similares_{query.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🤖 Búsqueda semántica con IA • "
        "ChromaDB"
    )


# Run the page function when this file is executed
if __name__ == "__main__":
    show_search_page()
