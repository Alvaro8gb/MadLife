"""
Search results visualization for MadLife Event Search Application.

This module provides the search results display with interactive elements
and quick actions for events.
"""

import streamlit as st
import pandas as pd
from .calendar_export import create_calendar_export_links, render_quick_calendar_button
from .events import display_event_detail


def navigate_to_event_detail(event_data):
    """
    Navigate to event detail page with proper session state handling.
    
    Args:
        event_data (dict): Event data to store in session state
    """
    st.session_state.selected_event = event_data
    # Use rerun instead of switch_page to trigger navigation
    st.rerun()


def display_search_results(results_df, query):
    """
    Display search results in a formatted way with interactive elements.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
        query (str): The search query used
    """
    if results_df.empty:
        st.warning("🔍 No se encontraron eventos similares para la búsqueda.")
        return

    _render_results_header(results_df, query)
    _render_results_list(results_df)


def _render_results_header(results_df, query):
    """Render the results header with query and count."""
    st.markdown(f"### 🎯 Resultados para: *'{query}'*")
    st.markdown(f"**{len(results_df)}** eventos encontrados")
    


def _render_results_list(results_df):
    """Render the list of search results."""
    for idx, row in results_df.iterrows():
        _render_single_result(row, idx)
        st.divider()


def _render_single_result(row, idx):
    """
    Render a single search result item.
    
    Args:
        row (pd.Series): Single row from results DataFrame
        idx (int): Index for unique key generation
    """
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            _render_result_main_content(row, idx)
        
        with col2:
            _render_result_metrics(row)
        
        with col3:
            _render_result_actions(row)


def _render_result_main_content(row, idx):
    """Render the main content of a search result."""
    # Make title clickable with better styling
    title_text = f"**{row['rank']}. {row['title']}**"
    
    # Create a more prominent clickable title
    col_title, col_icon = st.columns([4, 1])
    
    with col_title:
        if st.button(
            title_text, 
            key=f"event_{idx}", 
            help="Click para ver detalles completos del evento",
            use_container_width=True
        ):
            # Store the selected event in session state and navigate to detail page
            st.session_state.selected_event = row.to_dict()
            # Navigate to detail page using the correct page reference
            try:
                st.switch_page("pages/event_detail.py")
            except Exception as e:
                st.error(f"Error navegando: {e}")
                # Fallback: use session state flag
                st.session_state.navigate_to_detail = True
                st.rerun()
    
    with col_icon:
        st.markdown("👁️", help="Ver detalles")
    
    # Description preview
    if row.get('description_preview'):
        st.markdown(f"📝 {row['description_preview']}")
    
    # Event details
    details = _build_event_details(row)
    if details:
        st.markdown(" • ".join(details))
    
    # URL link
    if row.get('url'):
        st.markdown(f"[🔗 Más info]({row['url']})")


def _build_event_details(row):
    """Build the details list for an event."""
    details = []
    
    if row.get('date'):
        try:
            date_obj = pd.to_datetime(row['date'])
            details.append(f"📅 {date_obj.strftime('%d/%m/%Y')}")
        except Exception:
            details.append(f"📅 {row['date']}")
    
    if row.get('time'):
        details.append(f"⏰ {row['time']}")
    
    if row.get('district'):
        details.append(f"📍 {row['district']}")
    
    if row.get('venue'):
        details.append(f"🏢 {row['venue']}")
    
    return details


def _render_result_metrics(row):
    """Render metrics for a search result."""
    # Similarity score
    similarity_pct = row['similarity_score'] * 100
    st.metric("Similitud", f"{similarity_pct:.1f}%")
    
    # Free/Paid indicator
    if row.get('free') == '1':
        st.markdown("💚 **Gratuito**")
    elif row.get('free') == '0':
        st.markdown("💰 **De pago**")


def _render_result_actions(row):
    """Render action buttons for a search result."""
    # Event type
    if row.get('type'):
        type_clean = row['type'].split('/')[-1] if '/' in row['type'] else row['type']
        st.markdown(f"🏷️ **{type_clean}**")
    
    # View details button
    st.markdown("---")
    if st.button(
        "👁️ Ver detalles", 
        key=f"detail_btn_{row.name}", 
        use_container_width=True,
        type="secondary"
    ):
        st.toast("Accion")
        st.session_state.selected_event = row.to_dict()
        # Navigate to detail page using the correct page reference
        try:
            st.switch_page("pages/event_detail.py")
        except Exception as e:
            st.error(f"Error navegando: {e}")
            # Fallback: use session state flag
            st.session_state.navigate_to_detail = True
            st.rerun()
    
    # Quick calendar export button
    st.markdown("---")
    calendar_links = create_calendar_export_links(row.to_dict())
    quick_button_html = render_quick_calendar_button(calendar_links)
    st.markdown(quick_button_html, unsafe_allow_html=True)


def display_search_summary(results_df):
    """
    Display a summary of search results.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
    """
    if results_df.empty:
        return
    
    st.markdown("### 📈 Resumen de Resultados")
    
    # Average similarity
    avg_similarity = results_df['similarity_score'].mean()
    st.metric("Similitud Promedio", f"{avg_similarity:.2%}")
    
    # District distribution
    _display_district_summary(results_df)
    
    # Type distribution
    _display_type_summary(results_df)
    
    # Free vs Paid
    _display_price_summary(results_df)


def _display_district_summary(results_df):
    """Display district distribution summary."""
    if not results_df['district'].isna().all():
        district_counts = results_df['district'].value_counts().head(5)
        if len(district_counts) > 0:
            st.markdown("**🗺️ Distritos más relevantes:**")
            for district, count in district_counts.items():
                st.markdown(f"• {district}: {count} eventos")


def _display_type_summary(results_df):
    """Display event type distribution summary."""
    if not results_df['type'].isna().all():
        type_counts = results_df['type'].apply(
            lambda x: x.split('/')[-1] if pd.notna(x) and '/' in x else x
        ).value_counts().head(5)
        if len(type_counts) > 0:
            st.markdown("**🏷️ Tipos más comunes:**")
            for event_type, count in type_counts.items():
                if pd.notna(event_type):
                    st.markdown(f"• {event_type}: {count} eventos")


def _display_price_summary(results_df):
    """Display price distribution summary."""
    if not results_df['free'].isna().all():
        free_counts = results_df['free'].value_counts()
        if len(free_counts) > 0:
            st.markdown("**💰 Distribución de precios:**")
            free_count = free_counts.get('1', 0)
            paid_count = free_counts.get('0', 0)
            st.markdown(f"• Gratuitos: {free_count}")
            st.markdown(f"• De pago: {paid_count}")


def display_no_results_message(query):
    """
    Display a helpful message when no results are found.
    
    Args:
        query (str): The search query that returned no results
    """
    st.warning("🔍 No se encontraron eventos similares para la búsqueda.")
    
    with st.expander("💡 Sugerencias para mejorar tu búsqueda"):
        st.markdown("""
        - **Usa términos más generales**: en lugar de "concierto violín clásico", prueba "música clásica"
        - **Prueba sinónimos**: "teatro" o "obra", "exposición" o "muestra"
        - **Combina categorías**: "arte contemporáneo", "teatro infantil"
        - **Verifica filtros**: revisa si los filtros están limitando demasiado los resultados
        """)
        
        st.markdown("**Búsquedas populares:**")
        popular_queries = [
            "concierto música clásica",
            "teatro infantil",
            "exposición arte",
            "actividades deportivas",
            "talleres creativos",
            "flamenco"
        ]
        
        cols = st.columns(2)
        for i, example in enumerate(popular_queries):
            with cols[i % 2]:
                if st.button(f"🔎 {example}", key=f"suggestion_{i}"):
                    st.session_state.suggested_query = example
                    st.rerun()
