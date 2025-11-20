#!/usr/bin/env python3
"""Generate hybrid Europe+Africa dashboard"""

def generate_app():
    code = '''# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

st.set_page_config(
    page_title="Dashboard Environnemental",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-title {
    font-size: 2.8rem;
    font-weight: bold;
    color: #2E7D32;
    text-align: center;
}
.subtitle {
    font-size: 1.3rem;
    color: #555;
    text-align: center;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    base_path = Path(__file__).parent
    
    df_rec = pd.read_csv(base_path / 'municipal-waste-recycling-rate' / 'municipal-waste-recycling-rate.csv')
    df_was = pd.read_csv(base_path / 'total-waste-generation' / 'total-waste-generation.csv')
    
    df_rec = df_rec.rename(columns={
        'Entity': 'country', 'Code': 'country_code', 'Year': 'year',
        'Variable:% Recycling - MUNW': 'recycling_rate'
    })
    df_rec['year'] = df_rec['year'].astype(int)
    
    df_was = df_was.rename(columns={'Entity': 'country', 'Code': 'country_code', 'Year': 'year'})
    df_was['year'] = df_was['year'].astype(int)
    
    waste_cols = {}
    for col in df_was.columns:
        if 'households' in col.lower():
            waste_cols[col] = 'households_tonnes'
        elif 'construction' in col.lower():
            waste_cols[col] = 'construction_tonnes'
        elif 'manufacturing' in col.lower():
            waste_cols[col] = 'manufacturing_tonnes'
        elif 'services' in col.lower():
            waste_cols[col] = 'services_tonnes'
    
    df_was = df_was.rename(columns=waste_cols)
    wcols = [c for c in df_was.columns if c.endswith('_tonnes')]
    df_was['total_waste_tonnes'] = df_was[wcols].sum(axis=1, skipna=True)
    
    europe = ['France', 'Germany', 'Italy', 'Spain', 'Belgium', 'Netherlands',
              'Austria', 'Denmark', 'Sweden', 'Finland', 'Norway', 'Switzerland',
              'Poland', 'Portugal', 'Greece', 'Ireland', 'Czechia',
              'United Kingdom', 'Luxembourg', 'Slovenia', 'Slovakia']
    
    africa = ['Algeria', 'Egypt', 'Morocco', 'Tunisia', 'South Africa',
              'Kenya', 'Ghana', 'Botswana', 'Mauritius', 'Benin']
    
    europe = [c for c in europe if c in df_rec['country'].unique()]
    africa = [c for c in africa if c in df_was['country'].unique()]
    
    pop_dict = {
        'France': 67.4, 'Germany': 83.2, 'Italy': 59.6, 'Spain': 47.4,
        'Belgium': 11.5, 'Netherlands': 17.4, 'Austria': 8.9, 'Denmark': 5.8,
        'Sweden': 10.4, 'Finland': 5.5, 'Norway': 5.4, 'Switzerland': 8.6,
        'Poland': 38.0, 'Portugal': 10.3, 'Greece': 10.7, 'Ireland': 5.0,
        'Czechia': 10.7, 'United Kingdom': 67.1, 'Luxembourg': 0.63,
        'Slovenia': 2.1, 'Slovakia': 5.5,
        'Algeria': 43.9, 'Egypt': 102.3, 'Morocco': 36.9, 'Tunisia': 11.8,
        'South Africa': 59.3, 'Kenya': 53.8, 'Ghana': 31.1, 'Botswana': 2.4,
        'Mauritius': 1.3, 'Benin': 12.1
    }
    
    df_was['population_millions'] = df_was['country'].map(pop_dict)
    df_was['waste_per_capita_kg'] = (df_was['total_waste_tonnes'] * 1000 / 
                                      (df_was['population_millions'] * 1_000_000))
    
    rec_list = []
    for country in europe:
        cdata = df_rec[df_rec['country'] == country].copy()
        if len(cdata) > 0:
            yrs = range(cdata['year'].min(), cdata['year'].max() + 1)
            full_df = pd.DataFrame({'year': list(yrs), 'country': country})
            merged = pd.merge(full_df, cdata, on=['country', 'year'], how='left')
            merged['country_code'] = merged['country_code'].ffill().bfill()
            merged['recycling_rate'] = merged['recycling_rate'].interpolate(method='linear')
            rec_list.append(merged)
    
    df_rec_clean = pd.concat(rec_list, ignore_index=True) if rec_list else pd.DataFrame()
    
    df_merged = pd.merge(df_rec_clean, 
                        df_was[['country', 'year', 'total_waste_tonnes', 'waste_per_capita_kg']],
                        on=['country', 'year'], how='outer')
    
    return df_rec_clean, df_was, df_merged, europe, africa

with st.spinner('Chargement des donnees...'):
    df_recycling, df_waste, df_merged, europe_list, africa_list = load_data()

st.markdown('<p class="main-title">Dashboard Environnemental - Gestion des Dechets</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyse Comparative Europe & Afrique</p>', unsafe_allow_html=True)

st.info(f"""
🌍 **Dashboard Hybride**: 
- **Europe** ({len(europe_list)} pays): Recyclage + Generation (1990-2015)
- **Afrique** ({len(africa_list)} pays): Generation uniquement (2000-2021)
""")

st.sidebar.title("Filtres & Navigation")
st.sidebar.markdown("---")

region = st.sidebar.radio(
    "Region d'analyse",
    ["Europe (avec recyclage)", "Afrique (generation)", "Comparaison Nord-Sud"]
)

st.sidebar.markdown("### Pays a analyser")

if "Europe" in region:
    available = europe_list
    default_selection = ['France', 'Germany', 'Italy', 'Spain']
elif "Afrique" in region:
    available = africa_list
    default_selection = ['Algeria', 'Egypt', 'Morocco', 'Tunisia']
else:
    available = europe_list + africa_list
    default_selection = ['France', 'Germany', 'Algeria', 'Morocco']

default_selection = [c for c in default_selection if c in available][:4]

selected_countries = st.sidebar.multiselect(
    "Selectionner (max 10)",
    options=sorted(available),
    default=default_selection,
    max_selections=10
)

if not selected_countries:
    st.warning("⚠️ Selectionnez au moins un pays")
    st.stop()

st.sidebar.markdown("### Periode")

if "Europe" in region:
    available_years = sorted(df_recycling['year'].dropna().unique())
    default_year_range = (2010, 2015)
else:
    available_years = sorted(df_waste['year'].dropna().unique())
    default_year_range = (2010, int(max(available_years)))

year_range = st.sidebar.select_slider(
    "Plage d'annees",
    options=available_years,
    value=default_year_range
)

st.sidebar.markdown("---")

if "Afrique" in region:
    page = st.sidebar.radio("Navigation", [
        "Vue d'ensemble Afrique",
        "Production de Dechets",
        "Classement Africain",
        "Comparaisons"
    ])
else:
    page = st.sidebar.radio("Navigation", [
        "Vue d'ensemble & KPIs",
        "Tendances Temporelles",
        "Classements",
        "Analyse Geographique"
    ])

st.sidebar.markdown("---")
st.sidebar.info(f"""
**Selection:**
- {len(selected_countries)} pays
- Periode: {year_range[0]}-{year_range[1]}
""")

df_rec_filt = df_recycling[
    (df_recycling['country'].isin(selected_countries)) &
    (df_recycling['year'] >= year_range[0]) &
    (df_recycling['year'] <= year_range[1])
].copy()

df_waste_filt = df_waste[
    (df_waste['country'].isin(selected_countries)) &
    (df_waste['year'] >= year_range[0]) &
    (df_waste['year'] <= year_range[1])
].copy()

df_merged_filt = df_merged[
    (df_merged['country'].isin(selected_countries)) &
    (df_merged['year'] >= year_range[0]) &
    (df_merged['year'] <= year_range[1])
].copy()

if "Afrique" in region and page == "Vue d'ensemble Afrique":
    st.header("📊 Vue d'ensemble - Pays Africains")
    
    if len(df_waste_filt) == 0:
        st.error("Pas de donnees disponibles")
        st.stop()
    
    latest_year = df_waste_filt['year'].max()
    latest = df_waste_filt[df_waste_filt['year'] == latest_year]
    
    st.subheader("Indicateurs Cles")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_pc = latest['waste_per_capita_kg'].mean()
        st.metric("Production/Habitant", f"{avg_pc:.0f} kg/an")
    
    with col2:
        total_waste = latest['total_waste_tonnes'].sum()
        st.metric("Production Totale", f"{total_waste/1_000_000:.1f} M tonnes")
    
    with col3:
        max_idx = latest['waste_per_capita_kg'].idxmax()
        max_prod = latest.loc[max_idx, 'country']
        st.metric("Plus Producteur", max_prod)
    
    with col4:
        min_idx = latest['waste_per_capita_kg'].idxmin()
        min_prod = latest.loc[min_idx, 'country']
        st.metric("Moins Producteur", min_prod)
    
    st.markdown("---")
    st.subheader("Production par Habitant")
    
    sorted_latest = latest.sort_values('waste_per_capita_kg', ascending=False)
    
    fig = px.bar(
        sorted_latest,
        x='waste_per_capita_kg',
        y='country',
        orientation='h',
        title=f"Production de Dechets par Habitant ({int(latest_year)})",
        labels={'waste_per_capita_kg': 'kg/personne/an', 'country': 'Pays'},
        color='waste_per_capita_kg',
        color_continuous_scale='Reds'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Evolution Temporelle")
    
    fig2 = px.line(
        df_waste_filt,
        x='year',
        y='waste_per_capita_kg',
        color='country',
        title='Evolution de la Production par Habitant',
        labels={'year': 'Annee', 'waste_per_capita_kg': 'kg/personne/an', 'country': 'Pays'},
        markers=True
    )
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Vue d'ensemble & KPIs":
    st.header("📊 Indicateurs Cles de Performance")
    
    if "Europe" in region or region == "Comparaison Nord-Sud":
        valid_data = df_merged_filt.dropna(subset=['recycling_rate', 'waste_per_capita_kg'])
        
        if len(valid_data) > 0:
            latest_yr = valid_data['year'].max()
            latest_data = valid_data[valid_data['year'] == latest_yr]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_rec_rate = latest_data['recycling_rate'].mean()
                st.metric("Taux Recyclage Moyen", f"{avg_rec_rate:.1f}%")
            
            with col2:
                avg_waste_pc = latest_data['waste_per_capita_kg'].mean()
                st.metric("Dechets/Habitant", f"{avg_waste_pc:.0f} kg/an")
            
            with col3:
                best_idx = latest_data['recycling_rate'].idxmax()
                best_country = latest_data.loc[best_idx, 'country']
                st.metric("Meilleur Recyclage", best_country)
            
            with col4:
                countries_above_30 = len(latest_data[latest_data['recycling_rate'] > 30])
                st.metric("Pays >30%", f"{countries_above_30}/{len(selected_countries)}")
            
            st.markdown("---")
            st.subheader(f"Performance Environnementale ({int(latest_yr)})")
            
            fig = px.scatter(
                latest_data,
                x='waste_per_capita_kg',
                y='recycling_rate',
                size='total_waste_tonnes',
                color='recycling_rate',
                hover_name='country',
                title='Recyclage vs Production',
                labels={
                    'waste_per_capita_kg': 'Production (kg/hab/an)',
                    'recycling_rate': 'Taux Recyclage (%)',
                    'total_waste_tonnes': 'Total (tonnes)'
                },
                color_continuous_scale='RdYlGn',
                text='country'
            )
            fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Objectif 30%")
            fig.update_traces(textposition='top center')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Pas de donnees completes pour cette selection")

elif page == "Tendances Temporelles":
    st.header("📈 Evolution Temporelle")
    
    if len(df_rec_filt) > 0:
        fig = px.line(
            df_rec_filt,
            x='year',
            y='recycling_rate',
            color='country',
            title='Taux de Recyclage au Fil du Temps',
            labels={'year': 'Annee', 'recycling_rate': 'Taux (%)', 'country': 'Pays'},
            markers=True
        )
        fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Objectif 30%")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    if len(df_waste_filt) > 0:
        fig2 = px.line(
            df_waste_filt,
            x='year',
            y='waste_per_capita_kg',
            color='country',
            title='Production de Dechets par Habitant',
            labels={'year': 'Annee', 'waste_per_capita_kg': 'kg/hab/an', 'country': 'Pays'},
            markers=True
        )
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)

elif page in ["Classements", "Classement Africain"]:
    st.header("🏆 Classements")
    
    if "Afrique" in region:
        latest_yr = df_waste_filt['year'].max()
        latest_data = df_waste_filt[df_waste_filt['year'] == latest_yr]
        ranking = latest_data[['country', 'waste_per_capita_kg', 'total_waste_tonnes']].dropna()
        ranking = ranking.sort_values('waste_per_capita_kg')
        
        st.subheader(f"Classement par Production ({int(latest_yr)})")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                ranking.style.format({
                    'waste_per_capita_kg': '{:.0f} kg',
                    'total_waste_tonnes': '{:.0f}'
                }),
                use_container_width=True
            )
        
        with col2:
            st.markdown("### 🌿 Top 3 Moins Producteurs")
            for i in range(min(3, len(ranking))):
                row = ranking.iloc[i]
                st.success(f"{i+1}. **{row['country']}** - {row['waste_per_capita_kg']:.0f} kg/an")
    
    else:
        valid = df_merged_filt.dropna(subset=['recycling_rate', 'waste_per_capita_kg'])
        
        if len(valid) > 0:
            best_yr = valid.groupby('year')['country'].count().idxmax()
            ranking = valid[valid['year'] == best_yr]
            ranking = ranking[['country', 'recycling_rate', 'waste_per_capita_kg']].dropna()
            ranking = ranking.sort_values('recycling_rate', ascending=False)
            
            st.subheader(f"Classement par Recyclage ({int(best_yr)})")
            
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
                st.markdown("### 🏅 Podium")
                medals = ["🥇", "🥈", "🥉"]
                for i in range(min(3, len(ranking))):
                    row = ranking.iloc[i]
                    st.success(f"{medals[i]} **{row['country']}** - {row['recycling_rate']:.1f}%")

elif page == "Analyse Geographique":
    st.header("🗺️ Repartition Geographique")
    
    if len(df_rec_filt) > 0:
        latest_yr = df_rec_filt['year'].max()
        latest_data = df_rec_filt[df_rec_filt['year'] == latest_yr]
        
        fig = px.choropleth(
            latest_data,
            locations='country_code',
            color='recycling_rate',
            hover_name='country',
            title=f"Taux de Recyclage ({int(latest_yr)})",
            color_continuous_scale='RdYlGn',
            scope='europe'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("🚧 Page en construction")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
<p><strong>Dashboard Environnemental - Gestion des Dechets</strong></p>
<p>Sources: OECD, UN Environment | USTOMB 2025</p>
</div>
""", unsafe_allow_html=True)
'''
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    
    print("✅ app.py generated successfully!")
    print(f"📝 File size: {len(code)} characters")
    print("🚀 Run: streamlit run app.py")

if __name__ == '__main__':
    generate_app()
