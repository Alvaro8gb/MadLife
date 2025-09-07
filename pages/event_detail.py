"""
Event detail page for MadLife Event Search Application.
"""

import streamlit as st
from core.events import display_event_detail


def show_event_detail_page():
    """Display the event detail page with navigation back to search."""
    
    # Check if we have event data
    if 'selected_event' not in st.session_state or st.session_state.selected_event is None:
        st.error("No se encontró información del evento")
        if st.button("🔍 Ir a búsqueda", type="primary"):
            st.switch_page("pages/search.py")
        return
    
    # Breadcrumb navigation
    st.markdown("🔍 [Buscar Eventos](pages/search.py) → 🎭 Detalles del Evento")
    
    # Header with back button
    col_header1, col_header2 = st.columns([1, 4])
    
    with col_header1:
        if st.button("⬅️ Volver a búsqueda", type="primary", use_container_width=True):
            # Use st.switch_page to navigate back to search
            st.switch_page("pages/search.py")
    
    with col_header2:
        event_title = st.session_state.selected_event.get('title', 'Evento sin título')
        st.title(f"🎭 {event_title}")
    
    # Display the event detail
    display_event_detail(st.session_state.selected_event)
    
    # Additional navigation at the bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Volver atrás", use_container_width=True):
            st.switch_page("pages/search.py")
    with col2:
        if st.button("🔍 Nueva búsqueda", use_container_width=True):
            # Clear selected event and go back to search
            st.session_state.selected_event = None
            st.switch_page("pages/search.py")
    with col3:
        # Add a button to share or bookmark this event
        st.markdown("🔗 [Compartir evento](#)", help="URL para compartir este evento")


# Run the page function when this file is executed
if __name__ == "__main__":
    show_event_detail_page()
