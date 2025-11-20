"""
Export Charts Utility Script
Automatically generates high-quality PNG images of all key charts for use in reports and presentations.

Usage:
    python export_charts.py

This will create PNG files in the assets/ folder.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import numpy as np

# Set output directory
ASSETS_DIR = Path(__file__).parent / 'assets'
ASSETS_DIR.mkdir(exist_ok=True)

# Image settings
IMG_WIDTH = 1920  # HD width
IMG_HEIGHT = 1080  # HD height
IMG_SCALE = 2  # 2x for retina/high-DPI displays

print("=" * 80)
print("WASTE MANAGEMENT DASHBOARD - CHART EXPORT UTILITY")
print("=" * 80)
print(f"\nOutput directory: {ASSETS_DIR}")
print(f"Image settings: {IMG_WIDTH}x{IMG_HEIGHT} @ {IMG_SCALE}x scale\n")

# ==================== LOAD DATA ====================

print("Loading data...")

base_path = Path(__file__).parent

# Try to load cleaned data
try:
    df_waste = pd.read_csv(base_path / 'data' / 'clean_waste_generation.csv')
    df_recycling = pd.read_csv(base_path / 'data' / 'clean_recycling_rate.csv')
    df_waste_by_type = pd.read_csv(base_path / 'data' / 'clean_waste_by_type_algeria.csv')
    df_algeria_yoy = pd.read_csv(base_path / 'data' / 'algeria_waste_with_yoy.csv')
    print("✓ Cleaned data loaded successfully")
except FileNotFoundError:
    print("⚠ Cleaned data not found. Please run the data_prep.ipynb notebook first.")
    print("Attempting to load raw data...")
    
    # Load raw data
    waste_gen_raw = pd.read_csv(base_path / 'total-waste-generation' / 'total-waste-generation.csv')
    recycling_raw = pd.read_csv(base_path / 'municipal-waste-recycling-rate' / 'municipal-waste-recycling-rate.csv')
    
    # Basic processing (simplified)
    column_mapping_waste = {
        'Entity': 'country',
        'Code': 'country_code',
        'Year': 'year',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use': 'households_tonnes',
        '12.4.2 - Total waste generation, by activity (Tonnes) - EN_TWT_GENV - Other service activities': 'services_tonnes'
    }
    
    df_waste = waste_gen_raw.rename(columns=column_mapping_waste)
    df_waste = df_waste[df_waste['country'] == 'Algeria'].copy()
    df_waste['total_waste_tonnes'] = df_waste[['households_tonnes', 'services_tonnes']].sum(axis=1, skipna=True)
    
    # Add population (approximate)
    algeria_population = {
        2002: 31.36, 2005: 33.06, 2009: 35.27, 2014: 38.93, 2015: 39.54,
        2016: 40.15, 2017: 40.76, 2018: 41.39, 2019: 42.01, 2020: 42.64, 2021: 43.28
    }
    df_waste['population_millions'] = df_waste['year'].map(algeria_population)
    df_waste['waste_per_capita_kg_year'] = (
        df_waste['total_waste_tonnes'] * 1000 / (df_waste['population_millions'] * 1000000)
    )
    df_waste['waste_per_capita_kg_day'] = df_waste['waste_per_capita_kg_year'] / 365
    
    # YoY
    df_algeria_yoy = df_waste.sort_values('year').copy()
    df_algeria_yoy['yoy_change_percent'] = df_algeria_yoy['total_waste_tonnes'].pct_change() * 100
    
    # By type (simplified)
    df_waste_by_type = df_waste[['year', 'households_tonnes', 'services_tonnes']].melt(
        id_vars=['year'], var_name='waste_type', value_name='tonnes'
    )
    df_waste_by_type['waste_type'] = df_waste_by_type['waste_type'].str.replace('_tonnes', '').str.title()
    df_waste_by_type = df_waste_by_type.dropna()
    
    print("✓ Raw data processed")

algeria_data = df_waste[df_waste['country'] == 'Algeria'] if 'country' in df_waste.columns else df_waste

# ==================== CHART 1: TOTAL WASTE TREND ====================

print("\n1. Generating: Total Waste Trend (2002-2021)...")

fig1 = px.line(
    algeria_data,
    x='year',
    y='total_waste_tonnes',
    title='Évolution de la Production Totale de Déchets en Algérie (2002-2021)',
    labels={'year': 'Année', 'total_waste_tonnes': 'Déchets Totaux (Tonnes)'},
    markers=True
)

fig1.update_traces(
    line=dict(color='#1f77b4', width=4),
    marker=dict(size=12)
)

fig1.update_layout(
    font=dict(size=16),
    title_font_size=24,
    title_x=0.5,
    hovermode='x unified',
    plot_bgcolor='white',
    xaxis=dict(gridcolor='lightgray'),
    yaxis=dict(gridcolor='lightgray')
)

pio.write_image(fig1, ASSETS_DIR / 'chart1_total_waste_trend.png', 
                width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
print("   ✓ Saved: chart1_total_waste_trend.png")

# ==================== CHART 2: PER CAPITA ANNUAL ====================

print("2. Generating: Waste Per Capita (Annual)...")

algeria_pc_data = algeria_data[['year', 'waste_per_capita_kg_year']].dropna()

fig2 = px.line(
    algeria_pc_data,
    x='year',
    y='waste_per_capita_kg_year',
    title='Déchets par Habitant par An (kg/personne/an)',
    labels={'year': 'Année', 'waste_per_capita_kg_year': 'kg/personne/an'},
    markers=True
)

fig2.update_traces(
    line=dict(color='#ff7f0e', width=4),
    marker=dict(size=12)
)

fig2.update_layout(
    font=dict(size=16),
    title_font_size=24,
    title_x=0.5,
    hovermode='x',
    plot_bgcolor='white',
    xaxis=dict(gridcolor='lightgray'),
    yaxis=dict(gridcolor='lightgray')
)

pio.write_image(fig2, ASSETS_DIR / 'chart2_per_capita_annual.png',
                width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
print("   ✓ Saved: chart2_per_capita_annual.png")

# ==================== CHART 3: PER CAPITA DAILY ====================

print("3. Generating: Waste Per Capita (Daily)...")

algeria_pc_daily = algeria_data[['year', 'waste_per_capita_kg_day']].dropna()

fig3 = px.line(
    algeria_pc_daily,
    x='year',
    y='waste_per_capita_kg_day',
    title='Déchets par Habitant par Jour (kg/personne/jour)',
    labels={'year': 'Année', 'waste_per_capita_kg_day': 'kg/personne/jour'},
    markers=True
)

fig3.update_traces(
    line=dict(color='#2ca02c', width=4),
    marker=dict(size=12)
)

fig3.update_layout(
    font=dict(size=16),
    title_font_size=24,
    title_x=0.5,
    hovermode='x',
    plot_bgcolor='white',
    xaxis=dict(gridcolor='lightgray'),
    yaxis=dict(gridcolor='lightgray')
)

pio.write_image(fig3, ASSETS_DIR / 'chart3_per_capita_daily.png',
                width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
print("   ✓ Saved: chart3_per_capita_daily.png")

# ==================== CHART 4: YOY CHANGES ====================

print("4. Generating: Year-over-Year Changes...")

yoy_display = df_algeria_yoy[df_algeria_yoy['year'] >= 2003].copy()  # Skip first year

fig4 = go.Figure()

colors = ['green' if x > 0 else 'red' for x in yoy_display['yoy_change_percent']]

fig4.add_trace(go.Bar(
    x=yoy_display['year'],
    y=yoy_display['yoy_change_percent'],
    marker_color=colors,
    text=yoy_display['yoy_change_percent'].round(1),
    textposition='outside'
))

fig4.update_layout(
    title='Variation Annuelle de la Production de Déchets (%)',
    xaxis_title='Année',
    yaxis_title='Variation (%)',
    font=dict(size=16),
    title_font_size=24,
    title_x=0.5,
    plot_bgcolor='white',
    xaxis=dict(gridcolor='lightgray'),
    yaxis=dict(gridcolor='lightgray', zeroline=True, zerolinewidth=2, zerolinecolor='black'),
    showlegend=False
)

pio.write_image(fig4, ASSETS_DIR / 'chart4_yoy_changes.png',
                width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
print("   ✓ Saved: chart4_yoy_changes.png")

# ==================== CHART 5: PIE CHART BY TYPE ====================

print("5. Generating: Waste Composition (Pie Chart)...")

# Use latest year with data
latest_year = df_waste_by_type['year'].max()
waste_type_latest = df_waste_by_type[df_waste_by_type['year'] == latest_year]

fig5 = px.pie(
    waste_type_latest,
    values='tonnes',
    names='waste_type',
    title=f'Répartition des Déchets par Secteur ({int(latest_year)})',
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig5.update_traces(
    textposition='inside',
    textinfo='percent+label',
    textfont_size=16
)

fig5.update_layout(
    font=dict(size=16),
    title_font_size=24,
    title_x=0.5
)

pio.write_image(fig5, ASSETS_DIR / 'chart5_composition_pie.png',
                width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
print("   ✓ Saved: chart5_composition_pie.png")

# ==================== CHART 6: STACKED AREA ====================

print("6. Generating: Waste by Type Over Time (Stacked Area)...")

df_pivot = df_waste_by_type.pivot(index='year', columns='waste_type', values='tonnes').fillna(0)

fig6 = go.Figure()

for column in df_pivot.columns:
    fig6.add_trace(go.Scatter(
        x=df_pivot.index,
        y=df_pivot[column],
        mode='lines',
        name=column,
        stackgroup='one',
        line=dict(width=0.5)
    ))

fig6.update_layout(
    title='Production de Déchets Cumulée par Secteur au Fil du Temps',
    xaxis_title='Année',
    yaxis_title='Tonnes',
    font=dict(size=16),
    title_font_size=24,
    title_x=0.5,
    hovermode='x unified',
    plot_bgcolor='white',
    xaxis=dict(gridcolor='lightgray'),
    yaxis=dict(gridcolor='lightgray'),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

pio.write_image(fig6, ASSETS_DIR / 'chart6_stacked_area.png',
                width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
print("   ✓ Saved: chart6_stacked_area.png")

# ==================== CHART 7: BAR CHART BY TYPE ====================

print("7. Generating: Waste by Sector (Bar Chart)...")

waste_type_latest_sorted = waste_type_latest.sort_values('tonnes', ascending=True)

fig7 = px.bar(
    waste_type_latest_sorted,
    x='tonnes',
    y='waste_type',
    orientation='h',
    title=f'Volume de Déchets par Secteur ({int(latest_year)})',
    labels={'tonnes': 'Tonnes', 'waste_type': 'Secteur'},
    color='waste_type',
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig7.update_layout(
    font=dict(size=16),
    title_font_size=24,
    title_x=0.5,
    showlegend=False,
    plot_bgcolor='white',
    xaxis=dict(gridcolor='lightgray'),
    yaxis=dict(gridcolor='lightgray')
)

pio.write_image(fig7, ASSETS_DIR / 'chart7_composition_bar.png',
                width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
print("   ✓ Saved: chart7_composition_bar.png")

# ==================== SUMMARY ====================

print("\n" + "=" * 80)
print("EXPORT COMPLETE!")
print("=" * 80)
print(f"\n✓ 7 charts exported to: {ASSETS_DIR.absolute()}")
print("\nFiles created:")
print("  1. chart1_total_waste_trend.png       - For slides 4, report intro")
print("  2. chart2_per_capita_annual.png       - For report analysis section")
print("  3. chart3_per_capita_daily.png        - For report analysis section")
print("  4. chart4_yoy_changes.png             - For slides 4, report findings")
print("  5. chart5_composition_pie.png         - For slides 5, report composition")
print("  6. chart6_stacked_area.png            - For report detailed analysis")
print("  7. chart7_composition_bar.png         - For slides 5, report comparison")

print("\n📊 These charts are ready to use in:")
print("  - report.pdf (insert as images)")
print("  - slides.pptx (PowerPoint presentation)")
print("  - Any other documentation")

print("\n💡 Tips:")
print("  - Charts are high-resolution (HD @ 2x scale) for crisp display")
print("  - Suitable for both digital and print use")
print("  - Colors are consistent with dashboard theme")
print("  - All text is large and readable for presentations")

print("\n" + "=" * 80)
