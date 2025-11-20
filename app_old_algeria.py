"""
Gestion des déchets — Dashboard (Algérie)
Interactive Streamlit Dashboard for Waste Management Indicators

Author: Data Visualization Project
Date: October 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Waste Management Dashboard - Algeria",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .source-info {
        font-size: 0.8rem;
        color: #888;
        margin-top: 2rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING FUNCTIONS ====================

@st.cache_data
def load_data():
    """Load all cleaned datasets"""
    try:
        base_path = Path(__file__).parent / 'data'
        
        # Try to load cleaned data first
        waste_gen = pd.read_csv(base_path / 'clean_waste_generation.csv')
        recycling = pd.read_csv(base_path / 'clean_recycling_rate.csv')
        waste_by_type = pd.read_csv(base_path / 'clean_waste_by_type_algeria.csv')
        algeria_yoy = pd.read_csv(base_path / 'algeria_waste_with_yoy.csv')
        
        return waste_gen, recycling, waste_by_type, algeria_yoy, True
    except FileNotFoundError:
        # If cleaned data doesn't exist, load and process raw data
        return load_and_process_raw_data()

def load_and_process_raw_data():
    """Load and process raw data if cleaned data is not available"""
    base_path = Path(__file__).parent
    
    # Load raw data
    waste_gen_raw = pd.read_csv(base_path / 'total-waste-generation' / 'total-waste-generation.csv')
    recycling_raw = pd.read_csv(base_path / 'municipal-waste-recycling-rate' / 'municipal-waste-recycling-rate.csv')
    
    # Process waste generation data
    column_mapping_waste = {
        'Entity': 'country',
        'Code': 'country_code',
        'Year': 'year',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Agriculture, forestry and fishing': 'agriculture_tonnes',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use': 'households_tonnes',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Construction': 'construction_tonnes',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Manufacturing': 'manufacturing_tonnes',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Electricity, gas, steam and air conditioning supply': 'energy_tonnes',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Mining and quarrying': 'mining_tonnes',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Other service activities': 'services_tonnes'
    }
    
    waste_gen = waste_gen_raw.rename(columns=column_mapping_waste)
    
    # Process recycling data
    recycling = recycling_raw.rename(columns={
        'Entity': 'country',
        'Code': 'country_code',
        'Year': 'year',
        'Variable:% Recycling - MUNW': 'recycling_rate_percent'
    })
    
    # Filter for countries of interest
    countries_of_interest = ['Algeria', 'Morocco', 'Tunisia', 'Libya', 'Egypt', 
                             'France', 'Germany', 'Spain', 'Italy']
    
    waste_gen = waste_gen[waste_gen['country'].isin(countries_of_interest)].copy()
    recycling = recycling[recycling['country'].isin(countries_of_interest)].copy()
    
    # Calculate total waste
    waste_columns = ['agriculture_tonnes', 'households_tonnes', 'construction_tonnes', 
                     'manufacturing_tonnes', 'energy_tonnes', 'mining_tonnes', 'services_tonnes']
    waste_gen['total_waste_tonnes'] = waste_gen[waste_columns].sum(axis=1)
    
    # Add population data for Algeria (approximate from World Bank)
    algeria_population = {
        2002: 31.36, 2005: 33.06, 2009: 35.27, 2014: 38.93, 2015: 39.54,
        2016: 40.15, 2017: 40.76, 2018: 41.39, 2019: 42.01, 2020: 42.64, 2021: 43.28
    }
    
    waste_gen['population_millions'] = waste_gen.apply(
        lambda row: algeria_population.get(row['year'], np.nan) if row['country'] == 'Algeria' else np.nan,
        axis=1
    )
    
    # Calculate per capita metrics
    waste_gen['waste_per_capita_kg_year'] = (
        waste_gen['total_waste_tonnes'] * 1000 / (waste_gen['population_millions'] * 1000000)
    )
    waste_gen['waste_per_capita_kg_day'] = waste_gen['waste_per_capita_kg_year'] / 365
    
    # Create waste by type for Algeria
    algeria_waste = waste_gen[waste_gen['country'] == 'Algeria'].copy()
    waste_by_type = algeria_waste[['year', 'agriculture_tonnes', 'households_tonnes', 
                                     'construction_tonnes', 'manufacturing_tonnes', 
                                     'energy_tonnes', 'mining_tonnes', 'services_tonnes']].melt(
        id_vars=['year'],
        var_name='waste_type',
        value_name='tonnes'
    )
    waste_by_type['waste_type'] = waste_by_type['waste_type'].str.replace('_tonnes', '').str.title()
    waste_by_type = waste_by_type.dropna()
    
    # Calculate YoY changes
    algeria_yoy = waste_gen[waste_gen['country'] == 'Algeria'].sort_values('year').copy()
    algeria_yoy['yoy_change_tonnes'] = algeria_yoy['total_waste_tonnes'].diff()
    algeria_yoy['yoy_change_percent'] = algeria_yoy['total_waste_tonnes'].pct_change() * 100
    algeria_yoy['yoy_per_capita_change_percent'] = algeria_yoy['waste_per_capita_kg_year'].pct_change() * 100
    
    return waste_gen, recycling, waste_by_type, algeria_yoy, False

# Load data
try:
    df_waste, df_recycling, df_waste_by_type, df_algeria_yoy, data_cleaned = load_data()
    data_loaded = True
    
    # Show info if data is not cleaned
    if not data_cleaned:
        st.info("""
        ℹ️ **Astuce:** Pour de meilleures performances et toutes les fonctionnalités, exécutez le notebook de préparation des données:
        1. Ouvrez `notebooks/data_prep.ipynb` dans Jupyter Notebook
        2. Exécutez toutes les cellules
        3. Rechargez cette page
        
        Le dashboard fonctionne avec les données brutes, mais certaines métriques avancées seront disponibles après le nettoyage.
        """)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ==================== UTILITY FUNCTIONS ====================

def get_latest_value(df, country, column, year=None):
    """Get the latest or specific year value for a country"""
    country_data = df[df['country'] == country]
    if year:
        value = country_data[country_data['year'] == year][column].values
    else:
        value = country_data.sort_values('year', ascending=False)[column].values
    return value[0] if len(value) > 0 and not pd.isna(value[0]) else None

def format_number(num, decimals=0):
    """Format number with thousand separators"""
    if num is None or pd.isna(num):
        return "N/A"
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M"
    elif abs(num) >= 1_000:
        return f"{num/1_000:.{decimals}f}K"
    return f"{num:.{decimals}f}"

# ==================== HEADER ====================

st.markdown('<p class="main-header">♻️ Gestion des Déchets — Dashboard Algérie</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyse des Indicateurs de Production et de Recyclage des Déchets</p>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================

st.sidebar.title("🎛️ Contrôles")
st.sidebar.markdown("---")

# Get data ranges
algeria_data = df_waste[df_waste['country'] == 'Algeria']
min_year = int(algeria_data['year'].min())
max_year = int(algeria_data['year'].max())
available_years = sorted(algeria_data['year'].unique())

# Year selector
selected_year = st.sidebar.select_slider(
    "📅 Sélectionner l'année",
    options=available_years,
    value=max_year
)

# Country comparison selector
st.sidebar.markdown("### Comparaison avec d'autres pays")
available_countries = sorted(df_waste['country'].unique())
comparison_countries = st.sidebar.multiselect(
    "Pays à comparer",
    options=[c for c in available_countries if c != 'Algeria'],
    default=['Morocco', 'Tunisia'] if 'Morocco' in available_countries else []
)

# Page selector
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📊 Navigation",
    ["Vue d'ensemble", "Tendances Temporelles", "Composition des Déchets", "Comparaisons Internationales", "Insights & Recommandations"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"""
**À propos des données:**
- Source: Our World in Data (UN Environment Programme, OECD)
- Période: {min_year}-{max_year}
- Dernière mise à jour: Août 2024
""")

# ==================== PAGE 1: VUE D'ENSEMBLE ====================

if page == "Vue d'ensemble":
    st.header("📊 Vue d'ensemble — Indicateurs Clés")
    
    # Get latest data
    latest_year_data = algeria_data[algeria_data['year'] == selected_year]
    
    if len(latest_year_data) == 0:
        st.warning(f"Aucune donnée disponible pour l'année {selected_year}")
    else:
        latest_data = latest_year_data.iloc[0]
        
        # Calculate previous year for delta
        prev_year = selected_year - 1
        prev_data = algeria_data[algeria_data['year'] == prev_year]
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_waste = latest_data['total_waste_tonnes']
            delta_waste = None
            if len(prev_data) > 0:
                delta_waste = total_waste - prev_data.iloc[0]['total_waste_tonnes']
            
            st.metric(
                label="🗑️ Déchets Totaux",
                value=f"{format_number(total_waste, 1)} tonnes",
                delta=f"{format_number(delta_waste, 1)} tonnes" if delta_waste else None
            )
        
        with col2:
            per_capita_year = latest_data['waste_per_capita_kg_year']
            delta_pc = None
            if len(prev_data) > 0 and not pd.isna(prev_data.iloc[0]['waste_per_capita_kg_year']):
                delta_pc = per_capita_year - prev_data.iloc[0]['waste_per_capita_kg_year']
            
            st.metric(
                label="👤 Par Habitant/An",
                value=f"{format_number(per_capita_year, 1)} kg" if not pd.isna(per_capita_year) else "N/A",
                delta=f"{format_number(delta_pc, 1)} kg" if delta_pc else None
            )
        
        with col3:
            per_capita_day = latest_data['waste_per_capita_kg_day']
            st.metric(
                label="📅 Par Habitant/Jour",
                value=f"{format_number(per_capita_day, 2)} kg" if not pd.isna(per_capita_day) else "N/A"
            )
        
        with col4:
            # Get YoY change
            yoy_change = None
            if 'yoy_change_percent' in df_algeria_yoy.columns:
                yoy_data = df_algeria_yoy[df_algeria_yoy['year'] == selected_year]
                yoy_change = yoy_data['yoy_change_percent'].values[0] if len(yoy_data) > 0 else None
            
            st.metric(
                label="📈 Variation Annuelle",
                value=f"{format_number(yoy_change, 1)}%" if yoy_change and not pd.isna(yoy_change) else "N/A",
                delta=f"{format_number(yoy_change, 1)}%" if yoy_change and not pd.isna(yoy_change) else None
            )
        
        st.markdown("---")
        
        # Quick Summary
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Résumé des Données")
            
            households_waste = latest_data['households_tonnes']
            services_waste = latest_data['services_tonnes']
            
            st.write(f"""
            **Année sélectionnée:** {selected_year}
            
            **Déchets des ménages:** {format_number(households_waste)} tonnes ({format_number(households_waste/total_waste*100, 1)}% du total)
            
            **Déchets des services:** {format_number(services_waste) if not pd.isna(services_waste) else 'Non disponible'}
            
            **Population (estimée):** {format_number(latest_data['population_millions'], 2)} millions
            """)
        
        with col2:
            st.subheader("🎯 Points Clés")
            
            # Quick insights
            avg_growth = None
            if 'yoy_change_percent' in df_algeria_yoy.columns:
                avg_growth = df_algeria_yoy['yoy_change_percent'].mean()
            
            st.info(f"""
            ✓ {len(algeria_data)} années de données disponibles
            
            ✓ Croissance moyenne: {format_number(avg_growth, 1)}% par an
            
            ✓ Les déchets ménagers constituent la principale source de données
            """)
        
        # Trend mini chart
        st.markdown("---")
        st.subheader("📈 Évolution Récente (5 dernières années)")
        
        recent_data = algeria_data[algeria_data['year'] >= max_year - 4].sort_values('year')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recent_data['year'],
            y=recent_data['total_waste_tonnes'],
            mode='lines+markers',
            name='Déchets Totaux',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Production Totale de Déchets (Tonnes)",
            xaxis_title="Année",
            yaxis_title="Tonnes",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 2: TENDANCES TEMPORELLES ====================

elif page == "Tendances Temporelles":
    st.header("📈 Tendances Temporelles")
    
    # Waste generation over time
    st.subheader("Production de Déchets au Fil du Temps")
    
    # Prepare data for plotting
    countries_to_plot = ['Algeria'] + comparison_countries
    df_plot = df_waste[df_waste['country'].isin(countries_to_plot)].copy()
    
    # Total waste trend
    fig1 = px.line(
        df_plot,
        x='year',
        y='total_waste_tonnes',
        color='country',
        title='Évolution de la Production Totale de Déchets',
        labels={'year': 'Année', 'total_waste_tonnes': 'Déchets Totaux (Tonnes)', 'country': 'Pays'},
        markers=True
    )
    
    fig1.update_layout(
        hovermode='x unified',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Per capita trend
    st.subheader("Déchets par Habitant")
    
    algeria_pc_data = algeria_data[['year', 'waste_per_capita_kg_year', 'waste_per_capita_kg_day']].dropna()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig2 = px.line(
            algeria_pc_data,
            x='year',
            y='waste_per_capita_kg_year',
            title='Déchets par Habitant par An (kg)',
            markers=True
        )
        fig2.update_traces(line=dict(color='#ff7f0e', width=3))
        fig2.update_layout(hovermode='x', height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig3 = px.line(
            algeria_pc_data,
            x='year',
            y='waste_per_capita_kg_day',
            title='Déchets par Habitant par Jour (kg)',
            markers=True
        )
        fig3.update_traces(line=dict(color='#2ca02c', width=3))
        fig3.update_layout(hovermode='x', height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    # YoY Changes
    st.markdown("---")
    st.subheader("📊 Variations Annuelles")
    
    if 'yoy_change_percent' in df_algeria_yoy.columns:
        yoy_display = df_algeria_yoy[['year', 'total_waste_tonnes', 'yoy_change_tonnes', 'yoy_change_percent']].copy()
        yoy_display = yoy_display[yoy_display['year'] >= 2003]  # Skip first year (no YoY)
        
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=yoy_display['year'],
            y=yoy_display['yoy_change_percent'],
            name='Variation (%)',
            marker_color=['green' if x > 0 else 'red' for x in yoy_display['yoy_change_percent']]
        ))
        
        fig4.update_layout(
            title='Variation Annuelle en Pourcentage',
            xaxis_title='Année',
            yaxis_title='Variation (%)',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("💡 Les variations annuelles seront disponibles après avoir exécuté le notebook de préparation des données.")
    
    # Data table
    with st.expander("📋 Voir les données détaillées"):
        # Select available columns
        display_cols = ['year', 'total_waste_tonnes']
        if 'waste_per_capita_kg_year' in algeria_data.columns:
            display_cols.append('waste_per_capita_kg_year')
        if 'yoy_change_percent' in algeria_data.columns:
            display_cols.append('yoy_change_percent')
        if 'population_millions' in algeria_data.columns:
            display_cols.append('population_millions')
        
        st.dataframe(
            algeria_data[display_cols].sort_values('year', ascending=False),
            hide_index=True,
            use_container_width=True
        )

# ==================== PAGE 3: COMPOSITION DES DÉCHETS ====================

elif page == "Composition des Déchets":
    st.header("🗂️ Composition des Déchets par Type")
    
    # Filter by selected year
    waste_type_year = df_waste_by_type[df_waste_by_type['year'] == selected_year]
    
    if len(waste_type_year) == 0:
        st.warning(f"Aucune donnée de composition disponible pour {selected_year}")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                waste_type_year,
                values='tonnes',
                names='waste_type',
                title=f'Répartition des Déchets par Secteur ({selected_year})',
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart
            fig_bar = px.bar(
                waste_type_year.sort_values('tonnes', ascending=True),
                x='tonnes',
                y='waste_type',
                orientation='h',
                title=f'Volume de Déchets par Secteur ({selected_year})',
                labels={'tonnes': 'Tonnes', 'waste_type': 'Secteur'}
            )
            fig_bar.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Trend over time by type
    st.markdown("---")
    st.subheader("📈 Évolution par Secteur au Fil du Temps")
    
    fig_trend = px.line(
        df_waste_by_type,
        x='year',
        y='tonnes',
        color='waste_type',
        title='Évolution des Déchets par Secteur',
        markers=True,
        labels={'year': 'Année', 'tonnes': 'Tonnes', 'waste_type': 'Secteur'}
    )
    
    fig_trend.update_layout(
        hovermode='x unified',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Stacked area chart
    st.subheader("📊 Vue Cumulée")
    
    # Pivot data for stacked area
    df_pivot = df_waste_by_type.pivot(index='year', columns='waste_type', values='tonnes').fillna(0)
    
    fig_area = go.Figure()
    
    for column in df_pivot.columns:
        fig_area.add_trace(go.Scatter(
            x=df_pivot.index,
            y=df_pivot[column],
            mode='lines',
            name=column,
            stackgroup='one',
            fillcolor=None
        ))
    
    fig_area.update_layout(
        title='Production de Déchets Cumulée par Secteur',
        xaxis_title='Année',
        yaxis_title='Tonnes',
        hovermode='x unified',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_area, use_container_width=True)

# ==================== PAGE 4: COMPARAISONS INTERNATIONALES ====================

elif page == "Comparaisons Internationales":
    st.header("🌍 Comparaisons Internationales")
    
    if len(comparison_countries) == 0:
        st.info("👈 Sélectionnez des pays dans la barre latérale pour les comparer avec l'Algérie")
    else:
        # Compare selected year
        st.subheader(f"📊 Comparaison pour l'année {selected_year}")
        
        countries_compare = ['Algeria'] + comparison_countries
        compare_data = df_waste[
            (df_waste['country'].isin(countries_compare)) & 
            (df_waste['year'] == selected_year)
        ].copy()
        
        if len(compare_data) > 0:
            # Total waste comparison
            col1, col2 = st.columns(2)
            
            with col1:
                fig_comp1 = px.bar(
                    compare_data.sort_values('total_waste_tonnes', ascending=True),
                    x='total_waste_tonnes',
                    y='country',
                    orientation='h',
                    title='Déchets Totaux par Pays',
                    labels={'total_waste_tonnes': 'Tonnes', 'country': 'Pays'},
                    color='country'
                )
                fig_comp1.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_comp1, use_container_width=True)
            
            with col2:
                # Per capita comparison (only for countries with data)
                compare_pc = compare_data[compare_data['waste_per_capita_kg_year'].notna()]
                
                if len(compare_pc) > 0:
                    fig_comp2 = px.bar(
                        compare_pc.sort_values('waste_per_capita_kg_year', ascending=True),
                        x='waste_per_capita_kg_year',
                        y='country',
                        orientation='h',
                        title='Déchets par Habitant (kg/an)',
                        labels={'waste_per_capita_kg_year': 'kg/personne/an', 'country': 'Pays'},
                        color='country'
                    )
                    fig_comp2.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_comp2, use_container_width=True)
                else:
                    st.info("Données par habitant non disponibles pour tous les pays")
        
        # Time series comparison
        st.markdown("---")
        st.subheader("📈 Évolution Comparative")
        
        df_compare_time = df_waste[df_waste['country'].isin(countries_compare)].copy()
        
        fig_time_comp = px.line(
            df_compare_time,
            x='year',
            y='total_waste_tonnes',
            color='country',
            title='Évolution de la Production de Déchets - Comparaison Multi-Pays',
            markers=True,
            labels={'year': 'Année', 'total_waste_tonnes': 'Déchets Totaux (Tonnes)', 'country': 'Pays'}
        )
        
        fig_time_comp.update_layout(
            hovermode='x unified',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_time_comp, use_container_width=True)
        
        # Recycling rates comparison
        st.markdown("---")
        st.subheader("♻️ Taux de Recyclage (si disponible)")
        
        recycling_compare = df_recycling[df_recycling['country'].isin(countries_compare)]
        
        if len(recycling_compare) > 0:
            fig_recycling = px.line(
                recycling_compare,
                x='year',
                y='recycling_rate_percent',
                color='country',
                title='Évolution du Taux de Recyclage',
                markers=True,
                labels={'year': 'Année', 'recycling_rate_percent': 'Taux de Recyclage (%)', 'country': 'Pays'}
            )
            
            fig_recycling.update_layout(
                hovermode='x unified',
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_recycling, use_container_width=True)
            
            if 'Algeria' not in recycling_compare['country'].values:
                st.warning("⚠️ L'Algérie ne dispose pas de données de taux de recyclage dans le dataset OECD")
        else:
            st.info("Aucune donnée de taux de recyclage disponible pour les pays sélectionnés")

# ==================== PAGE 5: INSIGHTS & RECOMMANDATIONS ====================

elif page == "Insights & Recommandations":
    st.header("💡 Insights & Recommandations")
    
    # Calculate key statistics
    total_growth = ((algeria_data['total_waste_tonnes'].iloc[-1] - algeria_data['total_waste_tonnes'].iloc[0]) / 
                    algeria_data['total_waste_tonnes'].iloc[0] * 100)
    avg_waste_per_capita = algeria_data['waste_per_capita_kg_day'].mean()
    latest_waste_per_capita = algeria_data['waste_per_capita_kg_day'].iloc[-1]
    
    # Main Findings
    st.subheader("🔍 Principales Constatations")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        ### 📊 Analyse des Données ({min_year}-{max_year})
        
        **1. Croissance de la Production de Déchets**
        - La production totale de déchets a évolué de **{format_number(total_growth, 1)}%** sur la période
        - Les déchets ménagers constituent la source principale et la plus documentée
        - En {max_year}, l'Algérie a généré **{format_number(algeria_data.iloc[-1]['total_waste_tonnes'])} tonnes** de déchets
        
        **2. Production par Habitant**
        - Production moyenne: **{format_number(avg_waste_per_capita, 2)} kg/personne/jour**
        - Dernière valeur enregistrée: **{format_number(latest_waste_per_capita, 2)} kg/personne/jour** ({max_year})
        - Cette valeur est comparable aux pays en développement similaires
        
        **3. Composition des Déchets**
        - Les **déchets ménagers** dominent largement la production totale
        - Les données pour les autres secteurs (agriculture, construction, industrie) sont limitées
        - À partir de 2019, des données sur les **services** commencent à apparaître
        
        **4. Lacunes dans les Données**
        - ❌ Pas de données sur le **taux de recyclage** dans les datasets internationaux (OECD)
        - ❌ Données limitées sur la **composition détaillée** (plastique, organique, verre, etc.)
        - ❌ Absence de données géographiques par wilaya
        - ⚠️ Nécessité d'améliorer la collecte et le reporting des données
        """)
    
    with col2:
        # Visual summary
        st.metric(
            "📈 Croissance Totale",
            f"{format_number(total_growth, 1)}%",
            f"{min_year}-{max_year}"
        )
        
        st.metric(
            "👤 Déchets/Personne/Jour",
            f"{format_number(latest_waste_per_capita, 2)} kg",
            f"Année {max_year}"
        )
        
        st.metric(
            "📅 Années de Données",
            f"{len(algeria_data)}",
            f"{min_year}-{max_year}"
        )
    
    # Recommendations
    st.markdown("---")
    st.subheader("🎯 Recommandations")
    
    tab1, tab2, tab3 = st.tabs(["Gestion des Déchets", "Collecte de Données", "Recyclage & Valorisation"])
    
    with tab1:
        st.markdown("""
        ### 📋 Amélioration de la Gestion des Déchets
        
        1. **Tri à la Source**
           - Mettre en place des programmes de sensibilisation au tri sélectif
           - Distribuer des bacs de tri dans les zones urbaines
           - Former les citoyens aux bonnes pratiques
        
        2. **Infrastructure de Collecte**
           - Moderniser les systèmes de collecte existants
           - Étendre la couverture aux zones rurales
           - Optimiser les circuits de collecte
        
        3. **Traitement et Élimination**
           - Réduire la dépendance aux décharges
           - Développer des centres de tri modernes
           - Investir dans des technologies de traitement avancées
        
        4. **Réduction à la Source**
           - Promouvoir l'économie circulaire
           - Encourager l'éco-conception des produits
           - Limiter les emballages plastiques à usage unique
        """)
    
    with tab2:
        st.markdown("""
        ### 📊 Amélioration de la Collecte de Données
        
        1. **Standardisation**
           - Adopter les standards internationaux de reporting (OECD, UN)
           - Harmoniser les méthodes de mesure
           - Former les agents aux protocoles de collecte
        
        2. **Granularité**
           - Collecter des données par wilaya
           - Détailler par type de déchet (plastique, organique, verre, papier, etc.)
           - Suivre tous les secteurs (pas seulement les ménages)
        
        3. **Fréquence**
           - Passer à un reporting annuel systématique
           - Mettre en place un système de monitoring continu
           - Publier les données en open data
        
        4. **Indicateurs Clés**
           - Taux de recyclage
           - Taux de collecte
           - Taux de valorisation énergétique
           - Performance des infrastructures
        """)
    
    with tab3:
        st.markdown("""
        ### ♻️ Développement du Recyclage et de la Valorisation
        
        1. **Infrastructure de Recyclage**
           - Construire des centres de tri et de recyclage modernes
           - Créer des filières de recyclage par matériau
           - Soutenir les entreprises de recyclage
        
        2. **Compostage des Déchets Organiques**
           - Développer le compostage domestique
           - Créer des plateformes de compostage communautaires
           - Valoriser les déchets organiques en agriculture
        
        3. **Valorisation Énergétique**
           - Explorer les technologies de méthanisation
           - Étudier la faisabilité d'usines d'incinération avec récupération d'énergie
           - Capter le biogaz des décharges existantes
        
        4. **Économie Circulaire**
           - Créer des incitations économiques au recyclage
           - Développer les marchés de matières recyclées
           - Encourager les entreprises utilisant des matières recyclées
           - Mettre en place une REP (Responsabilité Élargie du Producteur)
        """)
    
    # Export options
    st.markdown("---")
    st.subheader("📥 Exporter les Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export Algeria data
        csv_algeria = algeria_data.to_csv(index=False)
        st.download_button(
            label="📊 Télécharger Données Algérie (CSV)",
            data=csv_algeria,
            file_name=f"algeria_waste_data_{min_year}_{max_year}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export waste by type
        if len(df_waste_by_type) > 0:
            csv_by_type = df_waste_by_type.to_csv(index=False)
            st.download_button(
                label="📁 Télécharger par Secteur (CSV)",
                data=csv_by_type,
                file_name=f"algeria_waste_by_type_{min_year}_{max_year}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Export YoY data
        csv_yoy = df_algeria_yoy.to_csv(index=False)
        st.download_button(
            label="📈 Télécharger Variations (CSV)",
            data=csv_yoy,
            file_name=f"algeria_waste_yoy_{min_year}_{max_year}.csv",
            mime="text/csv"
        )

# ==================== FOOTER ====================

st.markdown("---")
st.markdown(
    '<p class="source-info">'
    '📊 Sources: Our World in Data (UN Environment Programme, OECD) | '
    f'Dernière mise à jour: Août 2024 | '
    f'Dashboard créé: {datetime.now().strftime("%B %Y")}'
    '</p>',
    unsafe_allow_html=True
)
