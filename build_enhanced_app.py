#!/usr/bin/env python3
"""Generate enhanced multilingual dashboard with ML predictions"""

def generate_app():
    code = '''# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Environmental Dashboard - Waste Management",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
<style>
.main-title {
    font-size: 3rem;
    font-weight: bold;
    background: linear-gradient(120deg, #2E7D32, #66BB6A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0;
}
.subtitle {
    font-size: 1.4rem;
    color: #555;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border-left: 5px solid #2E7D32;
    margin: 10px 0;
}
.insight-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin: 15px 0;
}
.warning-box {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
.success-box {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    base_path = Path(__file__).parent
    
    df_rec = pd.read_csv(base_path / "municipal-waste-recycling-rate" / "municipal-waste-recycling-rate.csv")
    df_was = pd.read_csv(base_path / "total-waste-generation" / "total-waste-generation.csv")
    
    df_rec = df_rec.rename(columns={
        "Entity": "country", "Code": "country_code", "Year": "year",
        "Variable:% Recycling - MUNW": "recycling_rate"
    })
    df_rec["year"] = df_rec["year"].astype(int)
    
    df_was = df_was.rename(columns={"Entity": "country", "Code": "country_code", "Year": "year"})
    df_was["year"] = df_was["year"].astype(int)
    
    waste_cols = {}
    for col in df_was.columns:
        if "households" in col.lower() or "activities of households" in col.lower():
            waste_cols[col] = "households_tonnes"
        elif "construction" in col.lower():
            waste_cols[col] = "construction_tonnes"
        elif "manufacturing" in col.lower():
            waste_cols[col] = "manufacturing_tonnes"
        elif "other service" in col.lower():
            waste_cols[col] = "services_tonnes"
    
    df_was = df_was.rename(columns=waste_cols)
    wcols = [c for c in df_was.columns if c.endswith("_tonnes")]
    
    if wcols:
        df_was["total_waste_tonnes"] = df_was[wcols].sum(axis=1, skipna=True)
    else:
        numeric_cols = df_was.select_dtypes(include=[np.number]).columns
        numeric_cols = [c for c in numeric_cols if c not in ["year"]]
        if len(numeric_cols) > 0:
            df_was["total_waste_tonnes"] = df_was[numeric_cols].sum(axis=1, skipna=True)
        else:
            df_was["total_waste_tonnes"] = 0
    
    europe = ["France", "Germany", "Italy", "Spain", "Belgium", "Netherlands",
              "Austria", "Denmark", "Sweden", "Finland", "Norway", "Switzerland",
              "Poland", "Portugal", "Greece", "Ireland", "Czechia",
              "United Kingdom", "Luxembourg", "Slovenia", "Slovakia"]
    
    africa = ["Algeria", "Egypt", "Morocco", "Tunisia", "South Africa",
              "Kenya", "Ghana", "Botswana", "Mauritius", "Benin"]
    
    europe = [c for c in europe if c in df_rec["country"].unique()]
    africa = [c for c in africa if c in df_was["country"].unique()]
    
    pop_dict = {
        "France": 67.4, "Germany": 83.2, "Italy": 59.6, "Spain": 47.4,
        "Belgium": 11.5, "Netherlands": 17.4, "Austria": 8.9, "Denmark": 5.8,
        "Sweden": 10.4, "Finland": 5.5, "Norway": 5.4, "Switzerland": 8.6,
        "Poland": 38.0, "Portugal": 10.3, "Greece": 10.7, "Ireland": 5.0,
        "Czechia": 10.7, "United Kingdom": 67.1, "Luxembourg": 0.63,
        "Slovenia": 2.1, "Slovakia": 5.5,
        "Algeria": 43.9, "Egypt": 102.3, "Morocco": 36.9, "Tunisia": 11.8,
        "South Africa": 59.3, "Kenya": 53.8, "Ghana": 31.1, "Botswana": 2.4,
        "Mauritius": 1.3, "Benin": 12.1
    }
    
    df_was["population_millions"] = df_was["country"].map(pop_dict)
    mask = df_was["population_millions"].notna() & (df_was["total_waste_tonnes"] > 0)
    df_was.loc[mask, "waste_per_capita_kg"] = (
        df_was.loc[mask, "total_waste_tonnes"] * 1000 / 
        (df_was.loc[mask, "population_millions"] * 1_000_000)
    )
    
    africa_data = df_was[df_was["country"].isin(africa)].copy()
    
    if len(africa_data) > 0:
        for country in africa:
            country_data = africa_data[africa_data["country"] == country].copy()
            if len(country_data) > 0:
                year_min = africa_data["year"].min()
                year_max = africa_data["year"].max()
                
                full_years = pd.DataFrame({
                    "year": range(year_min, year_max + 1),
                    "country": country
                })
                
                country_full = pd.merge(full_years, country_data, 
                                       on=["year", "country"], how="left")
                
                country_full["country_code"] = country_data["country_code"].iloc[0] if len(country_data) > 0 else None
                country_full["population_millions"] = pop_dict.get(country)
                
                if country_full["total_waste_tonnes"].notna().sum() >= 2:
                    country_full["total_waste_tonnes"] = country_full["total_waste_tonnes"].interpolate(
                        method="linear", limit_direction="both"
                    )
                    
                    if country_full["population_millions"].iloc[0] > 0:
                        mask_calc = country_full["total_waste_tonnes"].notna()
                        country_full.loc[mask_calc, "waste_per_capita_kg"] = (
                            country_full.loc[mask_calc, "total_waste_tonnes"] * 1000 / 
                            (country_full.loc[mask_calc, "population_millions"] * 1_000_000)
                        )
                
                df_was = df_was[df_was["country"] != country]
                df_was = pd.concat([df_was, country_full], ignore_index=True)
    
    rec_list = []
    for country in europe:
        cdata = df_rec[df_rec["country"] == country].copy()
        if len(cdata) > 0:
            yrs = range(cdata["year"].min(), cdata["year"].max() + 1)
            full_df = pd.DataFrame({"year": list(yrs), "country": country})
            merged = pd.merge(full_df, cdata, on=["country", "year"], how="left")
            merged["country_code"] = merged["country_code"].ffill().bfill()
            merged["recycling_rate"] = merged["recycling_rate"].interpolate(method="linear")
            rec_list.append(merged)
    
    df_rec_clean = pd.concat(rec_list, ignore_index=True) if rec_list else pd.DataFrame()
    
    df_merged = pd.merge(df_rec_clean, 
                        df_was[["country", "year", "total_waste_tonnes", "waste_per_capita_kg"]],
                        on=["country", "year"], how="outer")
    
    return df_rec_clean, df_was, df_merged, europe, africa

def forecast_waste(df, country, years_ahead=5):
    """Simple linear regression forecast"""
    country_data = df[df["country"] == country].dropna(subset=["waste_per_capita_kg"])
    if len(country_data) < 3:
        return None
    
    X = country_data["year"].values.reshape(-1, 1)
    y = country_data["waste_per_capita_kg"].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    last_year = X.max()
    future_years = np.array(range(int(last_year) + 1, int(last_year) + years_ahead + 1)).reshape(-1, 1)
    predictions = model.predict(future_years)
    
    return pd.DataFrame({
        "year": future_years.flatten(),
        "predicted_waste_pc": predictions,
        "country": country
    })

def calculate_risk_score(recycling_rate, waste_pc, growth_rate):
    """Calculate environmental risk score (0-100)"""
    risk = 0
    
    if recycling_rate < 20:
        risk += 40
    elif recycling_rate < 30:
        risk += 25
    elif recycling_rate < 40:
        risk += 10
    
    if waste_pc > 600:
        risk += 30
    elif waste_pc > 500:
        risk += 20
    elif waste_pc > 400:
        risk += 10
    
    if growth_rate > 2:
        risk += 30
    elif growth_rate > 1:
        risk += 15
    elif growth_rate > 0:
        risk += 5
    
    return min(risk, 100)

with st.spinner("Loading data..."):
    df_recycling, df_waste, df_merged, europe_list, africa_list = load_data()

st.markdown('<p class="main-title">🌍 Environmental Dashboard - Waste Management</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Comparative Analysis: Europe & Africa</p>', unsafe_allow_html=True)

st.info(f"""
🌍 **Hybrid Dashboard**: 
- **Europe** ({len(europe_list)} countries): Recycling + Generation data (1990-2015)
- **Africa** ({len(africa_list)} countries): Generation data only (2000-2021)
- **ML Predictions**: Forecasting future waste trends
""")

st.sidebar.title("🎛️ Filters & Navigation")
st.sidebar.markdown("---")

region = st.sidebar.radio(
    "Analysis Region",
    ["Europe (with recycling)", "Africa (generation)", "North-South Comparison"]
)

st.sidebar.markdown("### 📍 Countries to Analyze")

if "Europe" in region:
    available = europe_list
    default_selection = ["France", "Germany", "Italy", "Spain"]
elif "Africa" in region:
    available = africa_list
    default_selection = ["Algeria", "Egypt", "Morocco", "Tunisia"]
else:
    available = europe_list + africa_list
    default_selection = ["France", "Germany", "Algeria", "Morocco"]

default_selection = [c for c in default_selection if c in available][:4]

selected_countries = st.sidebar.multiselect(
    "Select countries (max 10)",
    options=sorted(available),
    default=default_selection,
    max_selections=10
)

if not selected_countries:
    st.warning("⚠️ Please select at least one country")
    st.stop()

st.sidebar.markdown("### 📅 Time Period")

if "Europe" in region:
    available_years = sorted(df_recycling["year"].dropna().unique())
    default_year_range = (2010, 2015)
else:
    available_years = sorted(df_waste["year"].dropna().unique())
    default_year_range = (2010, int(max(available_years)))

year_range = st.sidebar.select_slider(
    "Year range",
    options=available_years,
    value=default_year_range
)

st.sidebar.markdown("---")

if "Africa" in region:
    page = st.sidebar.radio("📑 Navigation", [
        "Overview & KPIs",
        "Waste Production",
        "Geographic Analysis",
        "Rankings",
        "Predictions & Risks"
    ])
else:
    page = st.sidebar.radio("📑 Navigation", [
        "Overview & KPIs",
        "Temporal Trends",
        "Advanced Analytics",
        "Geographic Analysis",
        "Rankings",
        "Predictions & Risks"
    ])

st.sidebar.markdown("---")
st.sidebar.info(f"""
**Current Selection:**
- {len(selected_countries)} countries
- Period: {year_range[0]}-{year_range[1]}
""")

# Filter data
df_rec_filt = df_recycling[
    (df_recycling["country"].isin(selected_countries)) &
    (df_recycling["year"] >= year_range[0]) &
    (df_recycling["year"] <= year_range[1])
].copy()

df_waste_filt = df_waste[
    (df_waste["country"].isin(selected_countries)) &
    (df_waste["year"] >= year_range[0]) &
    (df_waste["year"] <= year_range[1])
].copy()

df_merged_filt = df_merged[
    (df_merged["country"].isin(selected_countries)) &
    (df_merged["year"] >= year_range[0]) &
    (df_merged["year"] <= year_range[1])
].copy()

# ============== PAGES ==============

if page == "Overview & KPIs":
    st.header("📊 Key Performance Indicators")
    
    if "Africa" in region:
        if len(df_waste_filt) == 0:
            st.error("No data available")
            st.stop()
        
        latest_year = df_waste_filt["year"].max()
        latest = df_waste_filt[df_waste_filt["year"] == latest_year]
        
        st.markdown(f"### 📅 Reference Year: **{int(latest_year)}**")
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_pc = latest["waste_per_capita_kg"].mean()
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                        padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">👤 Per Capita</h3>
                <h1 style="margin: 10px 0; font-size: 3rem; font-weight: bold;">{avg_pc:.0f}</h1>
                <p style="margin: 0; opacity: 0.9;">kg/person/year</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_waste = latest["total_waste_tonnes"].sum()
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%); 
                        padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">⚖️ Total Production</h3>
                <h1 style="margin: 10px 0; font-size: 3rem; font-weight: bold;">{total_waste/1_000_000:.1f}</h1>
                <p style="margin: 0; opacity: 0.9;">Million tonnes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            max_idx = latest["waste_per_capita_kg"].idxmax()
            max_prod = latest.loc[max_idx, "country"]
            max_val = latest.loc[max_idx, "waste_per_capita_kg"]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fd746c 0%, #ff9068 100%); 
                        padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">📈 Highest Producer</h3>
                <h1 style="margin: 10px 0; font-size: 2rem; font-weight: bold;">{max_prod}</h1>
                <p style="margin: 0; opacity: 0.9;">{max_val:.0f} kg/cap/yr</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            min_idx = latest["waste_per_capita_kg"].idxmin()
            min_prod = latest.loc[min_idx, "country"]
            min_val = latest.loc[min_idx, "waste_per_capita_kg"]
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">📉 Lowest Producer</h3>
                <h1 style="margin: 10px 0; font-size: 2rem; font-weight: bold;">{min_prod}</h1>
                <p style="margin: 0; opacity: 0.9;">{min_val:.0f} kg/cap/yr</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        sorted_latest = latest[latest["waste_per_capita_kg"].notna() & 
                              (latest["waste_per_capita_kg"] > 0)].copy()
        sorted_latest = sorted_latest.sort_values("waste_per_capita_kg", ascending=False)
        
        if len(sorted_latest) > 0:
            fig = px.bar(
                sorted_latest,
                x="waste_per_capita_kg",
                y="country",
                orientation="h",
                title=f"Waste Production per Capita ({int(latest_year)})",
                labels={"waste_per_capita_kg": "kg/person/year", "country": "Country"},
                color="waste_per_capita_kg",
                color_continuous_scale="Reds",
                text="waste_per_capita_kg"
            )
            fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            fig.update_layout(height=max(400, len(sorted_latest) * 30))
            st.plotly_chart(fig, use_container_width=True)
    
    else:  # Europe
        valid_data = df_merged_filt.dropna(subset=["recycling_rate", "waste_per_capita_kg"])
        
        if len(valid_data) > 0:
            latest_yr = valid_data["year"].max()
            latest_data = valid_data[valid_data["year"] == latest_yr]
            
            st.markdown(f"### 📅 Reference Year: **{int(latest_yr)}**")
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_rec_rate = latest_data["recycling_rate"].mean()
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;">
                    <h3 style="margin: 0; font-size: 1.2rem;">♻️ Recycling Rate</h3>
                    <h1 style="margin: 10px 0; font-size: 3rem; font-weight: bold;">{avg_rec_rate:.1f}%</h1>
                    <p style="margin: 0; opacity: 0.9;">Regional average</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_waste_pc = latest_data["waste_per_capita_kg"].mean()
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;">
                    <h3 style="margin: 0; font-size: 1.2rem;">🗑️ Production</h3>
                    <h1 style="margin: 10px 0; font-size: 3rem; font-weight: bold;">{avg_waste_pc:.0f}</h1>
                    <p style="margin: 0; opacity: 0.9;">kg/capita/year</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                best_idx = latest_data["recycling_rate"].idxmax()
                best_country = latest_data.loc[best_idx, "country"]
                best_rate = latest_data.loc[best_idx, "recycling_rate"]
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;">
                    <h3 style="margin: 0; font-size: 1.2rem;">🥇 Champion</h3>
                    <h1 style="margin: 10px 0; font-size: 2rem; font-weight: bold;">{best_country}</h1>
                    <p style="margin: 0; opacity: 0.9;">{best_rate:.1f}% recycling</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                countries_above_30 = len(latest_data[latest_data["recycling_rate"] > 30])
                pct_above = (countries_above_30 / len(selected_countries)) * 100
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;">
                    <h3 style="margin: 0; font-size: 1.2rem;">🎯 Target 30%</h3>
                    <h1 style="margin: 10px 0; font-size: 3rem; font-weight: bold;">{countries_above_30}/{len(selected_countries)}</h1>
                    <p style="margin: 0; opacity: 0.9;">{pct_above:.0f}% of countries</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                top5 = latest_data.nlargest(5, "recycling_rate")[["country", "recycling_rate"]]
                st.markdown("#### 🌟 Top 5 Recycling")
                for idx, row in top5.iterrows():
                    st.markdown(f"""
                    <div style="background: #f0f8ff; padding: 10px; margin: 5px 0; 
                                border-left: 4px solid #28a745; border-radius: 5px;">
                        <strong>{row["country"]}</strong>: {row["recycling_rate"]:.1f}%
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                bottom5 = latest_data.nsmallest(5, "recycling_rate")[["country", "recycling_rate"]]
                st.markdown("#### ⚠️ Top 5 to Improve")
                for idx, row in bottom5.iterrows():
                    st.markdown(f"""
                    <div style="background: #fff5f5; padding: 10px; margin: 5px 0; 
                                border-left: 4px solid #dc3545; border-radius: 5px;">
                        <strong>{row["country"]}</strong>: {row["recycling_rate"]:.1f}%
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader(f"📈 Environmental Performance ({int(latest_yr)})")
            
            fig = px.scatter(
                latest_data,
                x="waste_per_capita_kg",
                y="recycling_rate",
                size="total_waste_tonnes",
                color="recycling_rate",
                hover_name="country",
                title="Recycling vs Production",
                labels={
                    "waste_per_capita_kg": "Production (kg/cap/yr)",
                    "recycling_rate": "Recycling Rate (%)",
                    "total_waste_tonnes": "Total (tonnes)"
                },
                color_continuous_scale="RdYlGn",
                text="country"
            )
            fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="30% Target")
            fig.update_traces(textposition="top center")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No complete data for this selection")

elif page == "Advanced Analytics" and "Europe" in region:
    st.header("🔬 Advanced Analytics")
    
    valid_data = df_merged_filt.dropna(subset=["recycling_rate", "waste_per_capita_kg"])
    
    if len(valid_data) > 0:
        st.subheader("📊 Correlation Heatmap")
        
        pivot_rec = valid_data.pivot_table(
            values="recycling_rate",
            index="year",
            columns="country"
        )
        
        if pivot_rec.shape[1] > 1:
            corr_matrix = pivot_rec.corr()
            
            fig = px.imshow(
                corr_matrix,
                title="Country Recycling Rate Correlation Matrix",
                labels=dict(color="Correlation"),
                color_continuous_scale="RdBu",
                aspect="auto"
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="insight-box">
                <h4>💡 Insight</h4>
                <p>High correlation indicates similar recycling policies and economic development levels between countries.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📈 Trend Analysis")
        
        yearly_avg = valid_data.groupby("year").agg({
            "recycling_rate": "mean",
            "waste_per_capita_kg": "mean"
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Average Recycling Rate Over Time", "Average Waste per Capita Over Time"),
            vertical_spacing=0.12
        )
        
        fig.add_trace(
            go.Scatter(x=yearly_avg["year"], y=yearly_avg["recycling_rate"],
                      mode="lines+markers", name="Recycling Rate",
                      line=dict(color="#2E7D32", width=3)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=yearly_avg["year"], y=yearly_avg["waste_per_capita_kg"],
                      mode="lines+markers", name="Waste per Capita",
                      line=dict(color="#D32F2F", width=3)),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="kg/capita/year", row=2, col=1)
        fig.update_layout(height=700, showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🎯 Performance Quadrants")
        
        latest_yr = valid_data["year"].max()
        latest = valid_data[valid_data["year"] == latest_yr]
        
        median_rec = latest["recycling_rate"].median()
        median_waste = latest["waste_per_capita_kg"].median()
        
        latest["quadrant"] = latest.apply(
            lambda row: "High Rec / Low Waste" if row["recycling_rate"] > median_rec and row["waste_per_capita_kg"] < median_waste
                   else "High Rec / High Waste" if row["recycling_rate"] > median_rec
                   else "Low Rec / Low Waste" if row["waste_per_capita_kg"] < median_waste
                   else "Low Rec / High Waste",
            axis=1
        )
        
        fig = px.scatter(
            latest,
            x="waste_per_capita_kg",
            y="recycling_rate",
            color="quadrant",
            hover_name="country",
            title=f"Performance Quadrants ({int(latest_yr)})",
            labels={
                "waste_per_capita_kg": "Waste Production (kg/cap/yr)",
                "recycling_rate": "Recycling Rate (%)"
            },
            color_discrete_map={
                "High Rec / Low Waste": "#4CAF50",
                "High Rec / High Waste": "#FFC107",
                "Low Rec / Low Waste": "#2196F3",
                "Low Rec / High Waste": "#F44336"
            }
        )
        
        fig.add_hline(y=median_rec, line_dash="dash", line_color="gray")
        fig.add_vline(x=median_waste, line_dash="dash", line_color="gray")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Geographic Analysis":
    st.header("🗺️ Geographic Distribution")
    
    if "Africa" in region:
        st.subheader("🌍 African Countries - Waste Production")
        
        latest_year = df_waste_filt["year"].max()
        latest_data = df_waste_filt[df_waste_filt["year"] == latest_year].copy()
        latest_data = latest_data[latest_data["waste_per_capita_kg"].notna()]
        
        if len(latest_data) > 0:
            fig = px.choropleth(
                latest_data,
                locations="country_code",
                color="waste_per_capita_kg",
                hover_name="country",
                title=f"Waste Generation per Capita ({int(latest_year)})",
                color_continuous_scale="Reds",
                scope="africa",
                labels={"waste_per_capita_kg": "kg/capita/year"}
            )
            fig.update_layout(height=700, geo=dict(showframe=False, showcoastlines=True))
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📍 Country Details")
            
            display_data = latest_data[["country", "waste_per_capita_kg", "total_waste_tonnes", "population_millions"]]
            display_data = display_data.sort_values("waste_per_capita_kg", ascending=False)
            
            st.dataframe(
                display_data.style.format({
                    "waste_per_capita_kg": "{:.0f} kg",
                    "total_waste_tonnes": "{:.0f}",
                    "population_millions": "{:.1f}M"
                }).background_gradient(subset=["waste_per_capita_kg"], cmap="Reds"),
                use_container_width=True
            )
        else:
            st.warning("No geographic data available for selected period")
    
    else:  # Europe
        if len(df_rec_filt) > 0:
            latest_yr = df_rec_filt["year"].max()
            latest_data = df_rec_filt[df_rec_filt["year"] == latest_yr]
            
            fig = px.choropleth(
                latest_data,
                locations="country_code",
                color="recycling_rate",
                hover_name="country",
                title=f"Recycling Rate ({int(latest_yr)})",
                color_continuous_scale="RdYlGn",
                scope="europe",
                labels={"recycling_rate": "Recycling Rate (%)"}
            )
            fig.update_layout(height=700, geo=dict(showframe=False, showcoastlines=True))
            st.plotly_chart(fig, use_container_width=True)

elif page == "Predictions & Risks":
    st.header("🔮 Predictions & Risk Analysis")
    
    st.markdown("""
    <div class="insight-box">
        <h4>🤖 Machine Learning Predictions</h4>
        <p>Using linear regression to forecast waste generation trends for the next 5 years.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📈 Waste Production Forecasts")
    
    forecast_data = []
    for country in selected_countries:
        pred = forecast_waste(df_waste, country, years_ahead=5)
        if pred is not None:
            forecast_data.append(pred)
    
    if forecast_data:
        all_forecasts = pd.concat(forecast_data, ignore_index=True)
        
        historical = df_waste_filt[df_waste_filt["waste_per_capita_kg"].notna()]
        
        fig = go.Figure()
        
        for country in selected_countries:
            hist = historical[historical["country"] == country]
            if len(hist) > 0:
                fig.add_trace(go.Scatter(
                    x=hist["year"],
                    y=hist["waste_per_capita_kg"],
                    mode="lines+markers",
                    name=f"{country} (Historical)",
                    line=dict(width=2)
                ))
            
            pred = all_forecasts[all_forecasts["country"] == country]
            if len(pred) > 0:
                fig.add_trace(go.Scatter(
                    x=pred["year"],
                    y=pred["predicted_waste_pc"],
                    mode="lines+markers",
                    name=f"{country} (Predicted)",
                    line=dict(dash="dash", width=2)
                ))
        
        fig.update_layout(
            title="Waste Production: Historical Data & 5-Year Forecast",
            xaxis_title="Year",
            yaxis_title="Waste per Capita (kg/year)",
            height=600,
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚠️ Environmental Risk Assessment")
        
        if "Europe" in region:
            valid_data = df_merged_filt.dropna(subset=["recycling_rate", "waste_per_capita_kg"])
            if len(valid_data) > 0:
                risk_data = []
                for country in selected_countries:
                    country_data = valid_data[valid_data["country"] == country].sort_values("year")
                    if len(country_data) >= 2:
                        latest_rec = country_data.iloc[-1]["recycling_rate"]
                        latest_waste = country_data.iloc[-1]["waste_per_capita_kg"]
                        
                        first_waste = country_data.iloc[0]["waste_per_capita_kg"]
                        last_waste = country_data.iloc[-1]["waste_per_capita_kg"]
                        years_span = country_data.iloc[-1]["year"] - country_data.iloc[0]["year"]
                        
                        if years_span > 0 and first_waste > 0:
                            growth_rate = ((last_waste / first_waste) ** (1/years_span) - 1) * 100
                        else:
                            growth_rate = 0
                        
                        risk_score = calculate_risk_score(latest_rec, latest_waste, growth_rate)
                        
                        risk_data.append({
                            "country": country,
                            "recycling_rate": latest_rec,
                            "waste_per_capita": latest_waste,
                            "growth_rate": growth_rate,
                            "risk_score": risk_score,
                            "risk_level": "High" if risk_score > 60 else "Medium" if risk_score > 30 else "Low"
                        })
                
                if risk_data:
                    risk_df = pd.DataFrame(risk_data).sort_values("risk_score", ascending=False)
                    
                    fig = px.bar(
                        risk_df,
                        x="risk_score",
                        y="country",
                        orientation="h",
                        title="Environmental Risk Score by Country",
                        labels={"risk_score": "Risk Score (0-100)", "country": "Country"},
                        color="risk_score",
                        color_continuous_scale="RdYlGn_r",
                        text="risk_score"
                    )
                    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
                    fig.update_layout(height=max(400, len(risk_df) * 40))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("#### 📋 Detailed Risk Analysis")
                    
                    for _, row in risk_df.iterrows():
                        risk_color = "#F44336" if row["risk_level"] == "High" else "#FFC107" if row["risk_level"] == "Medium" else "#4CAF50"
                        st.markdown(f"""
                        <div style="background: {risk_color}; color: white; padding: 15px; 
                                    border-radius: 10px; margin: 10px 0;">
                            <h4 style="margin: 0;">{row["country"]} - {row["risk_level"]} Risk ({row["risk_score"]:.0f}/100)</h4>
                            <p style="margin: 5px 0;">♻️ Recycling Rate: {row["recycling_rate"]:.1f}%</p>
                            <p style="margin: 5px 0;">🗑️ Waste per Capita: {row["waste_per_capita"]:.0f} kg/year</p>
                            <p style="margin: 5px 0;">📈 Growth Rate: {row["growth_rate"]:.2f}% per year</p>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("Select countries with sufficient historical data for predictions")

elif page == "Temporal Trends":
    st.header("📈 Temporal Evolution")
    
    if len(df_rec_filt) > 0:
        fig = px.line(
            df_rec_filt,
            x="year",
            y="recycling_rate",
            color="country",
            title="Recycling Rate Over Time",
            labels={"year": "Year", "recycling_rate": "Rate (%)", "country": "Country"},
            markers=True
        )
        fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="30% Target")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    if len(df_waste_filt) > 0:
        df_waste_valid = df_waste_filt[df_waste_filt["waste_per_capita_kg"].notna() & 
                                       (df_waste_filt["waste_per_capita_kg"] > 0)].copy()
        
        if len(df_waste_valid) > 0:
            fig2 = px.line(
                df_waste_valid,
                x="year",
                y="waste_per_capita_kg",
                color="country",
                title="Waste Production per Capita",
                labels={"year": "Year", "waste_per_capita_kg": "kg/cap/yr", "country": "Country"},
                markers=True
            )
            fig2.update_layout(height=500)
            st.plotly_chart(fig2, use_container_width=True)

elif page == "Rankings":
    st.header("🏆 Rankings")
    
    if "Africa" in region:
        latest_yr = df_waste_filt["year"].max()
        latest_data = df_waste_filt[df_waste_filt["year"] == latest_yr]
        ranking = latest_data[["country", "waste_per_capita_kg", "total_waste_tonnes"]].dropna()
        ranking = ranking.sort_values("waste_per_capita_kg")
        
        st.subheader(f"Production Ranking ({int(latest_yr)})")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                ranking.style.format({
                    "waste_per_capita_kg": "{:.0f} kg",
                    "total_waste_tonnes": "{:.0f}"
                }),
                use_container_width=True
            )
        
        with col2:
            st.markdown("### 🌿 Top 3 Lowest Producers")
            for i in range(min(3, len(ranking))):
                row = ranking.iloc[i]
                st.success(f"{i+1}. **{row['country']}** - {row['waste_per_capita_kg']:.0f} kg/yr")
    
    else:
        valid = df_merged_filt.dropna(subset=["recycling_rate", "waste_per_capita_kg"])
        
        if len(valid) > 0:
            best_yr = valid.groupby("year")["country"].count().idxmax()
            ranking = valid[valid["year"] == best_yr]
            ranking = ranking[["country", "recycling_rate", "waste_per_capita_kg"]].dropna()
            ranking = ranking.sort_values("recycling_rate", ascending=False)
            
            st.subheader(f"Recycling Ranking ({int(best_yr)})")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(
                    ranking.style.format({
                        "recycling_rate": "{:.1f}%",
                        "waste_per_capita_kg": "{:.0f} kg"
                    }).background_gradient(subset=["recycling_rate"], cmap="RdYlGn"),
                    use_container_width=True
                )
            
            with col2:
                st.markdown("### 🏅 Podium")
                medals = ["🥇", "🥈", "🥉"]
                for i in range(min(3, len(ranking))):
                    row = ranking.iloc[i]
                    st.success(f"{medals[i]} **{row['country']}** - {row['recycling_rate']:.1f}%")

elif page == "Waste Production":
    st.header("📦 Waste Production - Detailed Analysis")
    
    if len(df_waste_filt) == 0:
        st.error("No data available")
        st.stop()
    
    st.subheader("📊 Total Production by Country")
    
    latest_year = df_waste_filt["year"].max()
    latest = df_waste_filt[df_waste_filt["year"] == latest_year]
    
    fig1 = px.bar(
        latest.sort_values("total_waste_tonnes", ascending=True),
        x="total_waste_tonnes",
        y="country",
        orientation="h",
        title=f"Total Waste Production ({int(latest_year)})",
        labels={"total_waste_tonnes": "Tonnes", "country": "Country"},
        color="total_waste_tonnes",
        color_continuous_scale="Oranges",
        text="total_waste_tonnes"
    )
    fig1.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📈 Production Evolution by Country")
    
    fig2 = px.line(
        df_waste_filt,
        x="year",
        y="total_waste_tonnes",
        color="country",
        title="Total Production Evolution",
        labels={"year": "Year", "total_waste_tonnes": "Tonnes", "country": "Country"},
        markers=True
    )
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("🚧 Page under construction")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
<p><strong>Environmental Dashboard - Waste Management Analysis</strong></p>
<p>Data Sources: OECD, UN Environment | USTOMB 2025</p>
<p>Powered by Machine Learning & Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)
'''
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    
    print("✅ Enhanced app.py generated successfully!")
    print(f"📝 File size: {len(code)} characters")
    print("🚀 Features:")
    print("   - English translation")
    print("   - ML forecasting (5-year predictions)")
    print("   - Risk assessment scoring")
    print("   - Geographic maps for Africa")
    print("   - Advanced analytics (correlation, quadrants)")
    print("   - Enhanced visual design")
    print("\n🎯 Run: streamlit run app.py")

if __name__ == '__main__':
    generate_app()
