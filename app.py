"""
MadLife Event Search - Streamlit Application

Interactive web application for searching events using semantic embeddings
with advanced filtering capabilities.
"""

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import time

import sys
import pysqlite3 as sqlite3
sys.modules['sqlite3'] = sqlite3

from embedding_manager import EventEmbeddingManager, create_embedding_database
from apiManager import load_madrid_events_data


st.set_page_config(
    page_title="MadLife",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_embedding_manager(df:pd.DataFrame):
    """Initialize the embedding manager with caching for better performance."""
    db_path = "./chroma_db"
    
    # Check if database exists
    if os.path.exists(db_path) and os.listdir(db_path):
        # Load existing database
        manager = EventEmbeddingManager(db_path=db_path)
        # Show success message briefly
        _placeholder = st.empty()
        _placeholder.success("✅ Base de datos de embeddings cargada correctamente!")
        time.sleep(2)
        _placeholder.empty()
    elif len(df) > 0:
        with st.spinner("Creando base de datos por primera vez..."):
            manager = create_embedding_database(df, db_path)
        
        # Show creation success message briefly
        _placeholder = st.empty()
        _placeholder.success("✅ Base de datos creada exitosamente!")
        time.sleep(3)
        _placeholder.empty()
    else:
        st.error(f"❌ Fallo al crear la base de datos")
        return None
    
    return manager

@st.cache_data
def load_raw_data():
    """Load raw CSV data for metadata analysis."""
    csv_path = "pruebas/data/300107-0-agenda-actividades-eventos.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path, sep=';', low_memory=False)
    return None

def extract_metadata_options(df):
    """Extract unique values for metadata filtering."""
    if df is None:
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
    """Create sidebar filters for metadata."""
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

def display_search_results(results_df, query):
    """Display search results in a formatted way."""
    if results_df.empty:
        st.warning("🔍 No se encontraron eventos similares para la búsqueda.")
        return
    
    st.markdown(f"### 🎯 Resultados para: *'{query}'*")
    st.markdown(f"**{len(results_df)}** eventos encontrados")
    
    # Display results
    for idx, row in results_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{row['rank']}. {row['title']}**")
                st.markdown(f"📝 {row['description_preview']}")
                
                # Event details
                details = []
                if row['date']:
                    try:
                        date_obj = pd.to_datetime(row['date'])
                        details.append(f"📅 {date_obj.strftime('%d/%m/%Y')}")
                    except:
                        details.append(f"📅 {row['date']}")
                
                if row['time']:
                    details.append(f"⏰ {row['time']}")
                
                if row['district']:
                    details.append(f"📍 {row['district']}")
                
                if row['venue']:
                    details.append(f"🏢 {row['venue']}")
                # URL link
                if row.get('url'):
                    # Render as clickable link opening in a new tab
                    st.markdown(f"[🔗 Más info]({row['url']})")
                
                st.markdown(" • ".join(details))
            
            with col2:
                # Similarity score
                similarity_pct = row['similarity_score'] * 100
                st.metric("Similitud", f"{similarity_pct:.1f}%")
                
                # Free/Paid indicator
                if row['free'] == '1':
                    st.markdown("💚 **Gratuito**")
                elif row['free'] == '0':
                    st.markdown("💰 **De pago**")
            
            with col3:
                # Event type
                if row['type']:
                    type_clean = row['type'].split('/')[-1] if '/' in row['type'] else row['type']
                    st.markdown(f"🏷️ **{type_clean}**")
        
        st.divider()

def create_similarity_chart(results_df):
    """Create a similarity score chart."""
    if results_df.empty:
        return
    
    fig = px.bar(
        results_df.head(10),
        x='similarity_score',
        y='title',
        orientation='h',
        title='Puntuación de Similitud (Top 10)',
        labels={'similarity_score': 'Puntuación de Similitud', 'title': 'Eventos'},
        color='similarity_score',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function."""
    
    # Header
    st.title("🎭 MadLife Buscador de Eventos")
    st.markdown("Busca el evento que mejor se adapte a ti")

    # Load raw data for metadata
    raw_df = load_madrid_events_data() #load_raw_data()
    print(raw_df.shape)
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
    
    # Date range filter (based on raw data FECHA column)
    try:
        date_series = pd.to_datetime(raw_df['FECHA'], errors='coerce')
        min_date = date_series.min().date() if not date_series.isna().all() else pd.to_datetime('today').date()
        max_date = date_series.max().date() if not date_series.isna().all() else pd.to_datetime('today').date()
    except Exception:
        min_date = pd.to_datetime('today').date()
        max_date = pd.to_datetime('today').date()

    st.sidebar.markdown("### 📅 Filtrar por fecha (fecha de inicio)")
 
    date_range = st.sidebar.date_input(
        "Intervalo de fechas:",
        value=(min_date, max_date),
        format="DD/MM/YYYY", # Formato de fecha
    )

    # Normalize date_range to two values
    if len(date_range) == 2:
        date_since, date_to = date_range[0], date_range[1]
    else:
        date_since = date_range
        date_to = date_range
    
    # Search configuration
    st.sidebar.markdown("### ⚙️ Configuración de Búsqueda")
    n_results = st.sidebar.slider("Número de resultados:", min_value=5, max_value=50, value=10)
    show_chart = st.sidebar.checkbox("Mostrar gráfico de similitud", value=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_input(
            "🔍 **Buscar eventos:**",
            placeholder="Ej: concierto música clásica, teatro infantil, exposición arte moderno...",
            help="Describe el tipo de evento que buscas en lenguaje natural"
        )
        
        st.markdown("**💡 Ejemplos de búsquedas:**")
        example_queries = [
            "concierto música clásica",
            "teatro infantil familiar",
            "exposición arte contemporáneo",
            "taller de cocina",
            "actividades deportivas",
            "festival flamenco"
        ]


        cols = st.columns(3)
        for i, example in enumerate(example_queries):
            with cols[i % 3]:
                if st.button(f"🔎 {example}", key=f"example_{i}"):
                    query = example
        
        # Search execution
        if query:
            with st.spinner("🔍 Buscando eventos similares..."):
               
                # Search for similar events
                results_df = manager.export_similar_events_df(
                    query=query,
                    n_results=n_results
                )
                
                
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

                dts = pd.to_datetime(date_since)
                dto = pd.to_datetime(date_to)
                results_df['date'] = pd.to_datetime(results_df['date'], errors='coerce')
                results_df = results_df[(results_df['date'] >= dts) & (results_df['date'] <= dto)]
            
                
                # Reset index after filtering
                results_df.reset_index(drop=True, inplace=True)
                results_df['rank'] = range(1, len(results_df) + 1)
            
            # Display results
            display_search_results(results_df, query)
    
    with col2:
        if query and not results_df.empty:

            st.markdown("### 📈 Resumen de Resultados")
            
            avg_similarity = results_df['similarity_score'].mean()
            st.metric("Similitud Promedio", f"{avg_similarity:.2%}")
            
            # District distribution
            if not results_df['district'].isna().all():
                district_counts = results_df['district'].value_counts().head(5)
                if len(district_counts) > 0:
                    st.markdown("**🗺️ Distritos más relevantes:**")
                    for district, count in district_counts.items():
                        st.markdown(f"• {district}: {count} eventos")
            
            # Type distribution
            if not results_df['type'].isna().all():
                type_counts = results_df['type'].apply(
                    lambda x: x.split('/')[-1] if pd.notna(x) and '/' in x else x
                ).value_counts().head(5)
                if len(type_counts) > 0:
                    st.markdown("**🏷️ Tipos más comunes:**")
                    for event_type, count in type_counts.items():
                        if pd.notna(event_type):
                            st.markdown(f"• {event_type}: {count} eventos")
            
            # Free vs Paid
            if not results_df['free'].isna().all():
                free_counts = results_df['free'].value_counts()
                if len(free_counts) > 0:
                    st.markdown("**💰 Distribución de precios:**")
                    free_count = free_counts.get('1', 0)
                    paid_count = free_counts.get('0', 0)
                    st.markdown(f"• Gratuitos: {free_count}")
                    st.markdown(f"• De pago: {paid_count}")
    
    # Similarity chart
    if query and show_chart and not results_df.empty:
        st.markdown("### 📊 Análisis de Similitud")
        create_similarity_chart(results_df)
    
    # Export functionality
    if query and not results_df.empty:
        st.markdown("### 💾 Exportar Resultados")
        
        # Prepare export data
        export_df = results_df[['rank', 'title', 'similarity_score', 'date', 'time', 
                               'district', 'venue', 'type', 'free', 'url']].copy()
        export_df.columns = ['Ranking', 'Título', 'Similitud', 'Fecha', 'Hora',
                           'Distrito', 'Lugar', 'Tipo', 'Gratuito', 'URL']
        
        csv_data = export_df.to_csv(index=False, encoding='utf-8')
        
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

if __name__ == "__main__":
    main()