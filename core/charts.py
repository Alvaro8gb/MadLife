"""
Charts and analytics visualizations for MadLife Event Search Application.

This module provides various chart components for data visualization
including similarity charts, distribution charts, and analytics.
"""

import streamlit as st
import plotly.express as px
import pandas as pd


def create_similarity_chart(results_df, key_prefix=""):
    """
    Create a similarity score chart for search results.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
        key_prefix (str): Prefix for the chart key to ensure uniqueness
    """
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
    
    st.plotly_chart(fig, use_container_width=True, key="similarity_chart")


def create_district_distribution_chart(results_df, key_prefix=""):
    """
    Create a district distribution pie chart.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
        key_prefix (str): Prefix for the chart key to ensure uniqueness
    """
    if results_df.empty or results_df['district'].isna().all():
        return
    
    district_counts = results_df['district'].value_counts().head(8)
    
    if len(district_counts) > 0:
        fig = px.pie(
            values=district_counts.values,
            names=district_counts.index,
            title='Distribución por Distritos'
        )
        
        fig.update_layout(height=400)
        chart_key = f"{key_prefix}district_distribution_chart" if key_prefix else "district_distribution_chart"
        st.plotly_chart(fig, use_container_width=True, key=chart_key)


def create_event_type_chart(results_df, key_prefix=""):
    """
    Create an event type distribution chart.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
        key_prefix (str): Prefix for the chart key to ensure uniqueness
    """
    if results_df.empty or results_df['type'].isna().all():
        return
    
    # Clean type names
    clean_types = results_df['type'].apply(
        lambda x: x.split('/')[-1] if pd.notna(x) and '/' in x else x
    ).value_counts().head(8)
    
    if len(clean_types) > 0:
        fig = px.bar(
            x=clean_types.index,
            y=clean_types.values,
            title='Tipos de Eventos Más Comunes',
            labels={'x': 'Tipo de Evento', 'y': 'Cantidad'}
        )
        
        fig.update_layout(
            height=400,
            xaxis_tickangle=-45
        )
        chart_key = f"{key_prefix}event_type_chart" if key_prefix else "event_type_chart"
        st.plotly_chart(fig, use_container_width=True, key=chart_key)


def create_free_vs_paid_chart(results_df, key_prefix=""):
    """
    Create a free vs paid events chart.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
        key_prefix (str): Prefix for the chart key to ensure uniqueness
    """
    if results_df.empty or results_df['free'].isna().all():
        return
    
    free_counts = results_df['free'].value_counts()
    
    if len(free_counts) > 0:
        labels = []
        values = []
        
        if '1' in free_counts.index:
            labels.append('Gratuitos')
            values.append(free_counts['1'])
        
        if '0' in free_counts.index:
            labels.append('De pago')
            values.append(free_counts['0'])
        
        if labels:
            fig = px.pie(
                values=values,
                names=labels,
                title='Distribución Gratuito vs De Pago',
                color_discrete_map={
                    'Gratuitos': '#28a745',
                    'De pago': '#ffc107'
                }
            )
            
            fig.update_layout(height=300)
            chart_key = f"{key_prefix}free_vs_paid_chart" if key_prefix else "free_vs_paid_chart"
            st.plotly_chart(fig, use_container_width=True, key=chart_key)


def create_timeline_chart(results_df, key_prefix=""):
    """
    Create a timeline chart showing events by date.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
        key_prefix (str): Prefix for the chart key to ensure uniqueness
    """
    if results_df.empty or results_df['date'].isna().all():
        return
    
    # Convert dates and group by date
    results_df_copy = results_df.copy()
    results_df_copy['date'] = pd.to_datetime(results_df_copy['date'], errors='coerce')
    results_df_copy = results_df_copy.dropna(subset=['date'])
    
    if results_df_copy.empty:
        return
    
    date_counts = results_df_copy.groupby(results_df_copy['date'].dt.date).size().reset_index()
    date_counts.columns = ['fecha', 'cantidad']
    
    if len(date_counts) > 0:
        fig = px.line(
            date_counts,
            x='fecha',
            y='cantidad',
            title='Eventos por Fecha',
            labels={'fecha': 'Fecha', 'cantidad': 'Número de Eventos'}, 
            markers=True
        )
        
        fig.update_layout(height=400)
        chart_key = f"{key_prefix}timeline_chart" if key_prefix else "timeline_chart"
        st.plotly_chart(fig, use_container_width=True, key=chart_key)


def display_summary_metrics(results_df):
    """
    Display summary metrics for search results.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
    """
    if results_df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(results_df)
        st.metric("📊 Total Eventos", total_events)
    
    with col2:
        avg_similarity = results_df['similarity_score'].mean()
        st.metric("🎯 Similitud Promedio", f"{avg_similarity:.1%}")
    
    with col3:
        free_events = len(results_df[results_df['free'] == '1'])
        st.metric("💚 Eventos Gratuitos", free_events)
    
    with col4:
        unique_districts = results_df['district'].nunique()
        st.metric("🗺️ Distritos", unique_districts)


def render_analytics_dashboard(results_df):
    """
    Render a complete analytics dashboard.
    
    Args:
        results_df (pd.DataFrame): DataFrame containing search results
    """
    if results_df.empty:
        st.warning("No hay datos para mostrar en el dashboard.")
        return
    
    st.markdown("### 📊 Dashboard de Análisis")
    
    # Summary metrics
    display_summary_metrics(results_df)
    
    # Charts in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Similitud", 
        "🗺️ Distritos", 
        "🏷️ Tipos", 
        "📅 Timeline"
    ])
    
    with tab1:
        create_similarity_chart(results_df, key_prefix="dashboard_")
    
    with tab2:
        create_district_distribution_chart(results_df, key_prefix="dashboard_")
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            create_event_type_chart(results_df, key_prefix="dashboard_")
        with col2:
            create_free_vs_paid_chart(results_df, key_prefix="dashboard_")
    
    with tab4:
        create_timeline_chart(results_df, key_prefix="dashboard_")
