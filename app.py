"""
MadLife Event Search - Streamlit Application

Interactive web application for searching events using semantic embeddings
with advanced filtering capabilities and detailed event visualization.
"""

import streamlit as st
from config import APP_CONFIG
from resourceManager import load_resources

# Configure Streamlit page
st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application function with multipage navigation."""
    
    logo = load_resources(APP_CONFIG["logo_path"])
    st.sidebar.write(logo, unsafe_allow_html=True)

    # Define pages
    search_page = st.Page("pages/search.py", title="Buscar Eventos", icon="🔍", default=True)
    event_detail_page = st.Page("pages/event_detail.py", title="Detalles del Evento", icon="🎭")
    
    # Create navigation
    pg = st.navigation([search_page, event_detail_page])
    
    # Run the selected page
    pg.run()


if __name__ == "__main__":
    main()
