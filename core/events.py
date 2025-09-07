"""
Event detail visualization for MadLife Event Search Application.

This module provides the detailed event view with comprehensive information
display and calendar export functionality.
"""

import streamlit as st
import pandas as pd
from .calendar_export import (
    create_calendar_export_links, 
    generate_ics_content,
    render_calendar_export_buttons
)


def display_event_detail(event_data):
    """
    Display detailed view of a selected event.
    
    Args:
        event_data (dict): Dictionary containing complete event information
    """
    # Create a prominent container for the event detail
    with st.container(border=True):
        
        # Event title
        st.markdown(f"## 🎭 {event_data.get('title', 'Evento sin título')}")
        
        # Main content in columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            _render_event_description(event_data)
            _render_event_datetime(event_data)
            _render_event_location(event_data)
            _render_event_type(event_data)
            _render_event_price(event_data)
            _render_event_links(event_data)
        
        with col2:
            _render_similarity_score(event_data)
            _render_calendar_export_section(event_data)


def _render_event_description(event_data):
    """Render event description section."""
    if event_data.get('description_preview'):
        st.markdown("**📝 Descripción:**")
        st.markdown(event_data['description_preview'])
        st.markdown("---")


def _render_event_datetime(event_data):
    """Render event date and time section."""
    st.markdown("**📅 Fecha y hora:**")
    date_time_info = []
    
    if event_data.get('date'):
        try:
            date_obj = pd.to_datetime(event_data['date'])
            date_time_info.append(f"📅 {date_obj.strftime('%A, %d de %B de %Y')}")
        except Exception:
            date_time_info.append(f"📅 {event_data['date']}")
    
    if event_data.get('time'):
        date_time_info.append(f"⏰ {event_data['time']}")
    
    if date_time_info:
        st.markdown(" • ".join(date_time_info))
    else:
        st.markdown("⚠️ Fecha no especificada")
    
    st.markdown("---")


def _render_event_location(event_data):
    """Render event location section."""
    st.markdown("**📍 Ubicación:**")
    location_info = []
    
    if event_data.get('venue'):
        location_info.append(f"🏢 {event_data['venue']}")
    if event_data.get('district'):
        location_info.append(f"🗺️ {event_data['district']}")
    
    if location_info:
        st.markdown(" • ".join(location_info))
    else:
        st.markdown("⚠️ Ubicación no especificada")
    
    st.markdown("---")


def _render_event_type(event_data):
    """Render event type section."""
    if event_data.get('type'):
        st.markdown("**🏷️ Tipo de evento:**")
        type_clean = event_data['type'].split('/')[-1] if '/' in event_data['type'] else event_data['type']
        st.markdown(type_clean)
        st.markdown("---")


def _render_event_price(event_data):
    """Render event price section."""
    st.markdown("**💰 Precio:**")
    if event_data.get('free') == '1':
        st.markdown("💚 **Gratuito**")
    elif event_data.get('free') == '0':
        st.markdown("💰 **De pago**")
    else:
        st.markdown("ℹ️ Consultar precio")
    
    st.markdown("---")


def _render_event_links(event_data):
    """Render external links section."""
    if event_data.get('url'):
        st.markdown("**🔗 Enlaces:**")
        st.markdown(f"[📄 Información oficial]({event_data['url']})")


def _render_similarity_score(event_data):
    """Render similarity score metric."""
    if event_data.get('similarity_score'):
        similarity_pct = event_data['similarity_score'] * 100
        st.metric("🎯 Similitud", f"{similarity_pct:.1f}%")


def _render_calendar_export_section(event_data):
    """Render calendar export section."""
    st.markdown("### 📅 Añadir al Calendario")
    
    calendar_links = create_calendar_export_links(event_data)
    
    # Calendar export buttons in a more compact layout
    calendar_buttons_html = render_calendar_export_buttons(calendar_links)
    st.markdown(calendar_buttons_html, unsafe_allow_html=True)
    
    # ICS file download (iCalendar format)
    st.markdown("---")
    ics_content = generate_ics_content(event_data)
    st.download_button(
        label="💾 Descargar .ics",
        data=ics_content,
        file_name=f"evento_{event_data['title'][:30].replace(' ', '_')}.ics",
        mime="text/calendar",
        help="Descarga el archivo .ics para importar en cualquier aplicación de calendario",
        use_container_width=True
    )


def display_event_preview(event_data, show_export_button=True):
    """
    Display a compact preview of an event (for use in lists).
    
    Args:
        event_data (dict): Dictionary containing event information
        show_export_button (bool): Whether to show quick export button
    """
    with st.container():
        # Event title and basic info
        st.markdown(f"**{event_data.get('title', 'Evento sin título')}**")
        
        if event_data.get('description_preview'):
            st.markdown(f"📝 {event_data['description_preview'][:100]}...")
        
        # Basic details in one line
        details = []
        if event_data.get('date'):
            try:
                date_obj = pd.to_datetime(event_data['date'])
                details.append(f"📅 {date_obj.strftime('%d/%m/%Y')}")
            except Exception:
                details.append(f"📅 {event_data['date']}")
        
        if event_data.get('time'):
            details.append(f"⏰ {event_data['time']}")
        
        if event_data.get('district'):
            details.append(f"📍 {event_data['district']}")
        
        if details:
            st.markdown(" • ".join(details))
        
        # Quick export button
        if show_export_button:
            calendar_links = create_calendar_export_links(event_data)
            st.markdown(f'<a href="{calendar_links["google"]}" target="_blank" style="text-decoration: none;"><small>📅 + Calendario</small></a>', unsafe_allow_html=True)
