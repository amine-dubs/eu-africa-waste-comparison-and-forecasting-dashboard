# Script pour construire app.py sans caracteres speciaux problematiques

content = """import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# Configuration
st.set_page_config(
    page_title="Dashboard Environnemental - Dechets",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown('''
    <style>
    .main-title {
        font-size: 2.8rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.3rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
''', unsafe_allow_html=True)

# Chargement des donnees
@st.cache_data
def load_and_process_data():
    base_path = Path(__file__).parent
    
    df_recycling = pd.read_csv(base_path / 'municipal-waste-recycling-rate' / 'municipal-waste-recycling-rate.csv')
    df_waste_gen = pd.read_csv(base_path / 'total-waste-generation' / 'total-waste-generation.csv')
    
    df_recycling = df_recycling.rename(columns={
        'Entity': 'country',
        'Code': 'country_code',
        'Year': 'year',
        'Variable:% Recycling - MUNW': 'recycling_rate'
    })
    
    df_waste_gen = df_waste_gen.rename(columns={
        'Entity': 'country',
        'Code': 'country_code',
        'Year': 'year'
    })
    
    waste_cols = {}
    for col in df_waste_gen.columns:
        if 'households' in col.lower():
            waste_cols[col] = 'households_tonnes'
        elif 'construction' in col.lower():
            waste_cols[col] = 'construction_tonnes'
        elif 'manufacturing' in col.lower():
            waste_cols[col] = 'manufacturing_tonnes'
        elif 'services' in col.lower():
            waste_cols[col] = 'services_tonnes'
        elif 'agriculture' in col.lower():
            waste_cols[col] = 'agriculture_tonnes'
        elif 'mining' in col.lower():
            waste_cols[col] = 'mining_tonnes'
        elif 'energy' in col.lower():
            waste_cols[col] = 'energy_tonnes'
    
    df_waste_gen = df_waste_gen.rename(columns=waste_cols)
    
    waste_columns = [c for c in df_waste_gen.columns if c.endswith('_tonnes')]
    df_waste_gen['total_waste_tonnes'] = df_waste_gen[waste_columns].sum(axis=1, skipna=True)
    
    focus_countries = [
        'France', 'Germany', 'Italy', 'Spain', 'Belgium', 'Netherlands',
        'Austria', 'Denmark', 'Sweden', 'Finland', 'Norway', 'Switzerland',
        'Poland', 'Portugal', 'Greece', 'Ireland', 'Czechia',
        'United Kingdom', 'Luxembourg', 'Slovenia', 'Slovakia'
    ]
    
    countries_with_recycling = df_recycling['country'].unique()
    focus_countries = [c for c in focus_countries if c in countries_with_recycling]
    
    df_recycling_filtered = df_recycling[df_recycling['country'].isin(focus_countries)].copy()
    df_waste_filtered = df_waste_gen[df_waste_gen['country'].isin(focus_countries)].copy()
    
    population_2020 = {
        'France': 67.4, 'Germany': 83.2, 'Italy': 59.6, 'Spain': 47.4,
        'Belgium': 11.5, 'Netherlands': 17.4, 'Austria': 8.9, 'Denmark': 5.8,
        'Sweden': 10.4, 'Finland': 5.5, 'Norway': 5.4, 'Switzerland': 8.6,
        'Poland': 38.0, 'Portugal': 10.3, 'Greece': 10.7, 'Ireland': 5.0,
        'Czechia': 10.7, 'United Kingdom': 67.1, 'Luxembourg': 0.63,
        'Slovenia': 2.1, 'Slovakia': 5.5
    }
    
    df_waste_filtered['population_millions'] = df_waste_filtered['country'].map(population_2020)
    df_waste_filtered['waste_per_capita_kg'] = (
        df_waste_filtered['total_waste_tonnes'] * 1000 / 
        (df_waste_filtered['population_millions'] * 1_000_000)
    )
    
    df_merged = pd.merge(
        df_recycling_filtered,
        df_waste_filtered[['country', 'year', 'total_waste_tonnes', 'waste_per_capita_kg', 
                           'households_tonnes', 'population_millions']],
        on=['country', 'year'],
        how='outer'
    )
    
    return df_recycling_filtered, df_waste_filtered, df_merged, focus_countries

with st.spinner('Chargement des donnees...'):
    df_recycling, df_waste, df_merged, countries_list = load_and_process_data()

# Header
st.markdown('<p class="main-title">Dashboard Environnemental - Gestion des Dechets</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyse Comparative Regionale | Pays Europeens & OCDE</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Filtres & Navigation")
st.sidebar.markdown("---")

st.sidebar.markdown("### Pays a Analyser")
selected_countries = st.sidebar.multiselect(
    "Selectionner pays (max 10)",
    options=sorted(countries_list),
    default=['France', 'Germany', 'Italy', 'Spain', 'Belgium', 'Netherlands'],
    max_selections=10
)

if not selected_countries:
    st.warning("Veuillez selectionner au moins un pays")
    st.stop()

st.sidebar.markdown("### Periode")
years_available = sorted(df_recycling['year'].dropna().unique())
year_range = st.sidebar.select_slider(
    "Plage d'annees",
    options=years_available,
    value=(2010, max(years_available))
)

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["Vue d'ensemble & KPIs", "Tendances Temporelles", "Classements & Comparaisons", 
     "Analyse Geographique", "Insights & Recommandations"]
)

st.sidebar.markdown("---")
st.sidebar.info(f'''
**Donnees:**
- {len(selected_countries)} pays selectionnes
- Periode: {year_range[0]}-{year_range[1]}
- Sources: OECD, UN Environment
''')

# Filtrage
df_recycling_filtered = df_recycling[
    (df_recycling['country'].isin(selected_countries)) &
    (df_recycling['year'] >= year_range[0]) &
    (df_recycling['year'] <= year_range[1])
].copy()

df_waste_filtered = df_waste[
    (df_waste['country'].isin(selected_countries)) &
    (df_waste['year'] >= year_range[0]) &
    (df_waste['year'] <= year_range[1])
].copy()

df_merged_filtered = df_merged[
    (df_merged['country'].isin(selected_countries)) &
    (df_merged['year'] >= year_range[0]) &
    (df_merged['year'] <= year_range[1])
].copy()

# Calcul KPIs
def calculate_kpis(df_recycling, df_waste, countries):
    kpis = {}
    
    latest_year = df_recycling['year'].max()
    latest_recycling = df_recycling[df_recycling['year'] == latest_year]
    kpis['avg_recycling_rate'] = latest_recycling['recycling_rate'].mean()
    kpis['best_recycler'] = latest_recycling.loc[latest_recycling['recycling_rate'].idxmax(), 'country']
    kpis['best_recycling_rate'] = latest_recycling['recycling_rate'].max()
    
    latest_waste = df_waste[df_waste['year'] == df_waste['year'].max()]
    kpis['avg_waste_per_capita'] = latest_waste['waste_per_capita_kg'].mean()
    kpis['lowest_producer'] = latest_waste.loc[latest_waste['waste_per_capita_kg'].idxmin(), 'country']
    kpis['lowest_waste_pc'] = latest_waste['waste_per_capita_kg'].min()
    
    first_year = max(df_recycling['year'].min(), latest_year - 10)
    recycling_start = df_recycling[df_recycling['year'] == first_year]['recycling_rate'].mean()
    recycling_end = df_recycling[df_recycling['year'] == latest_year]['recycling_rate'].mean()
    kpis['recycling_growth'] = ((recycling_end - recycling_start) / recycling_start * 100) if recycling_start > 0 else 0
    
    kpis['countries_above_30'] = len(latest_recycling[latest_recycling['recycling_rate'] > 30])
    kpis['total_countries'] = len(countries)
    
    waste_start = df_waste[df_waste['year'] == df_waste['year'].min()]['total_waste_tonnes'].sum()
    waste_end = df_waste[df_waste['year'] == df_waste['year'].max()]['total_waste_tonnes'].sum()
    kpis['waste_generation_growth'] = ((waste_end - waste_start) / waste_start * 100) if waste_start > 0 else 0
    
    return kpis

kpis = calculate_kpis(df_recycling_filtered, df_waste_filtered, selected_countries)

# PAGE 1
if page == "Vue d'ensemble & KPIs":
    st.header("Indicateurs Cles de Performance (KPIs)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="KPI 1: Taux Recyclage Moyen",
            value=f"{kpis['avg_recycling_rate']:.1f}%",
            delta=f"{kpis['recycling_growth']:.1f}% sur 10 ans"
        )
    
    with col2:
        st.metric(
            label="KPI 2: Dechets/Habitant",
            value=f"{kpis['avg_waste_per_capita']:.0f} kg/an",
            delta=f"Meilleur: {kpis['lowest_waste_pc']:.0f} kg",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="KPI 3: Croissance Recyclage",
            value=f"+{kpis['recycling_growth']:.1f}%",
            delta="Evolution 10 ans"
        )
    
    with col4:
        st.metric(
            label="KPI 4: Performance Collective",
            value=f"{kpis['countries_above_30']}/{kpis['total_countries']}",
            delta="Pays >30% recyclage"
        )
    
    with col5:
        st.metric(
            label="KPI 5: Generation Dechets",
            value=f"{kpis['waste_generation_growth']:+.1f}%",
            delta="Evolution totale",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Champions du Recyclage")
        
        latest_year = df_recycling_filtered['year'].max()
        top_recyclers = df_recycling_filtered[
            df_recycling_filtered['year'] == latest_year
        ].nlargest(5, 'recycling_rate')
        
        fig = px.bar(
            top_recyclers,
            x='recycling_rate',
            y='country',
            orientation='h',
            title=f'Top 5 Taux de Recyclage ({int(latest_year)})',
            labels={'recycling_rate': 'Taux de Recyclage (%)', 'country': 'Pays'},
            color='recycling_rate',
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Production par Habitant")
        
        latest_waste = df_waste_filtered[
            df_waste_filtered['year'] == df_waste_filtered['year'].max()
        ].nsmallest(5, 'waste_per_capita_kg')
        
        fig2 = px.bar(
            latest_waste,
            x='waste_per_capita_kg',
            y='country',
            orientation='h',
            title='Top 5 Plus Faibles Producteurs (kg/pers/an)',
            labels={'waste_per_capita_kg': 'kg/personne/an', 'country': 'Pays'},
            color='waste_per_capita_kg',
            color_continuous_scale='Blues_r'
        )
        fig2.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    st.subheader(f"Snapshot {int(latest_year)}")
    
    snapshot = df_merged_filtered[df_merged_filtered['year'] == latest_year].copy()
    snapshot = snapshot[['country', 'recycling_rate', 'waste_per_capita_kg', 'total_waste_tonnes']].dropna()
    
    fig_snapshot = px.scatter(
        snapshot,
        x='waste_per_capita_kg',
        y='recycling_rate',
        size='total_waste_tonnes',
        color='recycling_rate',
        hover_name='country',
        title='Performance Environnementale: Recyclage vs Production',
        labels={
            'waste_per_capita_kg': 'Production par Habitant (kg/an)',
            'recycling_rate': 'Taux de Recyclage (%)',
            'total_waste_tonnes': 'Total (tonnes)'
        },
        color_continuous_scale='RdYlGn',
        size_max=60
    )
    fig_snapshot.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Objectif 30%")
    fig_snapshot.update_layout(height=500)
    st.plotly_chart(fig_snapshot, use_container_width=True)

# PAGE 2
elif page == "Tendances Temporelles":
    st.header("Evolution Temporelle des Indicateurs")
    
    st.subheader("Evolution du Taux de Recyclage")
    
    fig1 = px.line(
        df_recycling_filtered,
        x='year',
        y='recycling_rate',
        color='country',
        title='Taux de Recyclage par Pays au Fil du Temps',
        labels={'year': 'Annee', 'recycling_rate': 'Taux de Recyclage (%)', 'country': 'Pays'},
        markers=True
    )
    fig1.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Objectif 30%")
    fig1.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Tendances Moyennes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_by_year = df_recycling_filtered.groupby('year')['recycling_rate'].mean().reset_index()
        
        fig2 = px.area(
            avg_by_year,
            x='year',
            y='recycling_rate',
            title='Taux de Recyclage Moyen Regional',
            labels={'year': 'Annee', 'recycling_rate': 'Taux Moyen (%)'},
            color_discrete_sequence=['#2E7D32']
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        if not df_waste_filtered.empty and 'waste_per_capita_kg' in df_waste_filtered.columns:
            avg_waste = df_waste_filtered.groupby('year')['waste_per_capita_kg'].mean().reset_index()
            
            fig3 = px.area(
                avg_waste,
                x='year',
                y='waste_per_capita_kg',
                title='Production Moyenne par Habitant',
                labels={'year': 'Annee', 'waste_per_capita_kg': 'kg/personne/an'},
                color_discrete_sequence=['#D32F2F']
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Donnees de production par habitant limitees")

# PAGE 3
elif page == "Classements & Comparaisons":
    st.header("Classements et Comparaisons")
    
    latest_year = df_recycling_filtered['year'].max()
    
    st.subheader(f"Classement General ({int(latest_year)})")
    
    ranking = df_merged_filtered[df_merged_filtered['year'] == latest_year].copy()
    ranking = ranking[['country', 'recycling_rate', 'waste_per_capita_kg']].dropna()
    ranking = ranking.sort_values('recycling_rate', ascending=False).reset_index(drop=True)
    ranking.index = ranking.index + 1
    ranking.index.name = 'Rang'
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(
            ranking.style.format({
                'recycling_rate': '{:.1f}%',
                'waste_per_capita_kg': '{:.0f} kg'
            }).background_gradient(subset=['recycling_rate'], cmap='RdYlGn'),
            use_container_width=True
        )
    
    with col2:
        st.markdown("### Podium")
        if len(ranking) >= 1:
            st.success(f"**{ranking.iloc[0]['country']}** - {ranking.iloc[0]['recycling_rate']:.1f}%")
        if len(ranking) >= 2:
            st.info(f"**{ranking.iloc[1]['country']}** - {ranking.iloc[1]['recycling_rate']:.1f}%")
        if len(ranking) >= 3:
            st.warning(f"**{ranking.iloc[2]['country']}** - {ranking.iloc[2]['recycling_rate']:.1f}%")

# PAGE 4
elif page == "Analyse Geographique":
    st.header("Repartition Geographique")
    
    latest_year = df_recycling_filtered['year'].max()
    map_data = df_recycling_filtered[df_recycling_filtered['year'] == latest_year].copy()
    
    st.subheader(f"Carte du Taux de Recyclage ({int(latest_year)})")
    
    fig_map = px.choropleth(
        map_data,
        locations='country_code',
        color='recycling_rate',
        hover_name='country',
        hover_data={'recycling_rate': ':.1f%', 'country_code': False},
        title='Taux de Recyclage par Pays',
        color_continuous_scale='RdYlGn',
        range_color=[0, 60],
        scope='europe'
    )
    fig_map.update_geos(
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="lightgray"
    )
    fig_map.update_layout(height=600)
    st.plotly_chart(fig_map, use_container_width=True)

# PAGE 5
elif page == "Insights & Recommandations":
    st.header("Insights et Recommandations Environnementales")
    
    st.subheader("Principaux Constats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
        ### Forces Identifiees
        
        - Plusieurs pays depassent 40% de recyclage
        - Tendance generale a la hausse (+{kpis['recycling_growth']:.1f}% sur 10 ans)
        - Les pays nordiques menent la region
        ''')
    
    with col2:
        st.markdown('''
        ### Defis a Relever
        
        - Disparites importantes entre pays
        - Production par habitant encore elevee
        - Certains pays sous le seuil de 30%
        ''')
    
    st.markdown("---")
    st.subheader("Exporter les Donnees")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_recycling = df_recycling_filtered.to_csv(index=False)
        st.download_button(
            label="Donnees Recyclage (CSV)",
            data=csv_recycling,
            file_name=f"recyclage_data_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv"
        )
    
    with col2:
        csv_waste = df_waste_filtered.to_csv(index=False)
        st.download_button(
            label="Donnees Production (CSV)",
            data=csv_waste,
            file_name=f"waste_generation_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv"
        )
    
    with col3:
        kpi_report = pd.DataFrame([kpis]).T
        kpi_report.columns = ['Valeur']
        csv_kpis = kpi_report.to_csv()
        st.download_button(
            label="Rapport KPIs (CSV)",
            data=csv_kpis,
            file_name="kpis_report.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown('''
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p><strong>Dashboard Environnemental - Gestion des Dechets</strong></p>
    <p>Sources: OECD, UN Environment Programme</p>
    <p>USTOMB/FMI/INF/ING4/SD/DataViz | Enseignante: F. Guerroudji</p>
    <p>Derniere mise a jour: Novembre 2025</p>
</div>
''', unsafe_allow_html=True)
"""

# Ecrire le fichier
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fichier app.py cree avec succes!")
