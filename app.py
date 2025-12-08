# -*- coding: utf-8 -*-
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
from statsmodels.tsa.arima.model import ARIMA
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
    
    # Expanded to 27 European countries with recycling data
    europe = ["France", "Germany", "Italy", "Spain", "Belgium", "Netherlands",
              "Austria", "Denmark", "Sweden", "Finland", "Norway", "Switzerland",
              "Poland", "Portugal", "Greece", "Ireland", "Czechia",
              "United Kingdom", "Luxembourg", "Slovenia", "Slovakia",
              "Estonia", "Hungary", "Iceland", "Latvia", "Lithuania", "Turkey"]
    
    # Expanded to 22 African countries with waste data
    africa = ["Algeria", "Egypt", "Morocco", "Tunisia", "South Africa",
              "Kenya", "Ghana", "Botswana", "Mauritius", "Benin",
              "Burkina Faso", "Burundi", "Cape Verde", "Guinea", "Lesotho",
              "Madagascar", "Niger", "Sudan", "Tanzania", "Togo", "Zambia", "Zimbabwe"]
    
    europe = [c for c in europe if c in df_rec["country"].unique()]
    africa = [c for c in africa if c in df_was["country"].unique()]
    
    pop_dict = {
        # European countries (27 total)
        "France": 67.4, "Germany": 83.2, "Italy": 59.6, "Spain": 47.4,
        "Belgium": 11.5, "Netherlands": 17.4, "Austria": 8.9, "Denmark": 5.8,
        "Sweden": 10.4, "Finland": 5.5, "Norway": 5.4, "Switzerland": 8.6,
        "Poland": 38.0, "Portugal": 10.3, "Greece": 10.7, "Ireland": 5.0,
        "Czechia": 10.7, "United Kingdom": 67.1, "Luxembourg": 0.63,
        "Slovenia": 2.1, "Slovakia": 5.5,
        "Estonia": 1.3, "Hungary": 9.7, "Iceland": 0.37, "Latvia": 1.9,
        "Lithuania": 2.8, "Turkey": 84.3,
        # African countries (22 total)
        "Algeria": 43.9, "Egypt": 102.3, "Morocco": 36.9, "Tunisia": 11.8,
        "South Africa": 59.3, "Kenya": 53.8, "Ghana": 31.1, "Botswana": 2.4,
        "Mauritius": 1.3, "Benin": 12.1,
        "Burkina Faso": 20.9, "Burundi": 11.9, "Cape Verde": 0.56, "Guinea": 13.1,
        "Lesotho": 2.1, "Madagascar": 27.7, "Niger": 24.2, "Sudan": 43.8,
        "Tanzania": 59.7, "Togo": 8.3, "Zambia": 18.4, "Zimbabwe": 14.9
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
    
    # Interpolate waste data for European countries (fill missing odd years)
    europe_data = df_was[df_was["country"].isin(europe)].copy()
    
    if len(europe_data) > 0:
        for country in europe:
            country_data = europe_data[europe_data["country"] == country].copy()
            if len(country_data) > 0 and len(country_data) >= 2:
                year_min = country_data["year"].min()
                year_max = country_data["year"].max()
                
                # Create full year range
                full_years = pd.DataFrame({
                    "year": range(year_min, year_max + 1),
                    "country": country
                })
                
                country_full = pd.merge(full_years, country_data, 
                                       on=["year", "country"], how="left")
                
                country_full["country_code"] = country_data["country_code"].iloc[0] if len(country_data) > 0 else None
                country_full["population_millions"] = pop_dict.get(country)
                
                # Interpolate total waste
                if country_full["total_waste_tonnes"].notna().sum() >= 2:
                    country_full["total_waste_tonnes"] = country_full["total_waste_tonnes"].interpolate(
                        method="linear", limit_direction="both"
                    )
                    
                    # Recalculate waste per capita
                    if country_full["population_millions"].iloc[0] and country_full["population_millions"].iloc[0] > 0:
                        mask_calc = country_full["total_waste_tonnes"].notna()
                        country_full.loc[mask_calc, "waste_per_capita_kg"] = (
                            country_full.loc[mask_calc, "total_waste_tonnes"] * 1000 / 
                            (country_full.loc[mask_calc, "population_millions"] * 1_000_000)
                        )
                
                # Remove old data and add interpolated data
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

def forecast_waste(df, country, years_ahead=5, window_size=5):
    """
    ARIMA time series forecast using actual waste values to predict future waste.
    Uses autoregressive patterns in the data rather than just year-based linear regression.
    
    Args:
        df: DataFrame with waste data
        country: Country name
        years_ahead: Number of years to forecast
        window_size: Number of recent years to use for training (default 5)
    
    Returns:
        DataFrame with predictions and 'model_used' column
    """
    country_data = df[df["country"] == country].dropna(subset=["waste_per_capita_kg"])
    country_data = country_data.sort_values("year")
    
    if len(country_data) < 3:
        return None
    
    # Use only the most recent window_size years for better trend capture
    if len(country_data) > window_size:
        country_data = country_data.tail(window_size)
    
    y = country_data["waste_per_capita_kg"].values
    last_year = int(country_data["year"].max())
    
    try:
        # ARIMA(p,d,q): p=autoregressive order, d=differencing, q=moving average
        # (1,1,1) is a good default for most time series with trends
        model = ARIMA(y, order=(1, 1, 1))
        fitted_model = model.fit()
        
        # Forecast future values
        predictions = fitted_model.forecast(steps=years_ahead)
        
        # Ensure predictions are non-negative
        predictions = np.maximum(predictions, 0)
        
        future_years = np.array(range(last_year + 1, last_year + years_ahead + 1))
        
        return pd.DataFrame({
            "year": future_years,
            "predicted_waste_pc": predictions,
            "country": country,
            "model_used": "ARIMA"
        })
    except Exception as e:
        # Fallback to simple linear regression if ARIMA fails
        X = country_data["year"].values.reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)
        
        future_years = np.array(range(last_year + 1, last_year + years_ahead + 1)).reshape(-1, 1)
        predictions = model.predict(future_years)
        predictions = np.maximum(predictions, 0)
        
        return pd.DataFrame({
            "year": future_years.flatten(),
            "predicted_waste_pc": predictions,
            "country": country,
            "model_used": "Linear Regression (fallback)"
        })

def calculate_risk_score(recycling_rate, waste_pc, growth_rate):
    """Calculate environmental risk score (0-100) for countries with recycling data"""
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

def calculate_risk_score_africa(waste_pc, growth_rate, waste_total_millions):
    """Calculate environmental risk score (0-100) for African countries without recycling data"""
    risk = 0
    
    # No recycling infrastructure assumed = base risk
    risk += 35
    
    # High waste per capita
    if waste_pc > 400:
        risk += 25
    elif waste_pc > 300:
        risk += 15
    elif waste_pc > 200:
        risk += 5
    
    # High growth rate
    if growth_rate > 3:
        risk += 30
    elif growth_rate > 2:
        risk += 20
    elif growth_rate > 1:
        risk += 10
    elif growth_rate > 0:
        risk += 5
    
    # Large total waste volume (infrastructure pressure)
    if waste_total_millions > 10:
        risk += 10
    elif waste_total_millions > 5:
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

if "Africa" in region and "Comparison" not in region:
    # Africa only - use waste data years (2000-2021)
    available_years = sorted(df_waste["year"].dropna().unique())
    default_year_range = (2010, int(max(available_years)))
elif "Europe" in region and "Comparison" not in region:
    # Europe only - use waste data years (2000-2021) for full data range
    # Note: Recycling data only goes to 2015, but waste data extends to 2020+
    available_years = sorted(df_waste["year"].dropna().unique())
    default_year_range = (2010, int(max(available_years)))
else:
    # North-South Comparison - use full waste data years (2000-2021)
    # Note: Recycling data only goes to 2015, but waste data (which is what we forecast) extends to 2020+
    # For waste forecasting, we need the full waste data range, not just recycling overlap
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
    
    elif "Europe" in region and "Comparison" not in region:  # Europe only (not North-South)
        # Use recycling data directly (already interpolated) and merge with waste data (also interpolated)
        valid_rec = df_rec_filt.dropna(subset=["recycling_rate"])
        valid_waste = df_waste_filt.dropna(subset=["waste_per_capita_kg"])
        
        # Inner join since both datasets now have interpolated odd years
        valid_data = pd.merge(valid_rec, valid_waste[["country", "year", "waste_per_capita_kg", "total_waste_tonnes"]], 
                             on=["country", "year"], how="inner")
        
        if len(valid_data) > 0:
            latest_yr = valid_data["year"].max()
            latest_data = valid_data[valid_data["year"] == latest_yr]
            
            st.markdown(f"### 📅 Reference Year: **{int(latest_yr)}**")
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_rec_rate = latest_data["recycling_rate"].mean()
                # Green gradient for recycling (positive environmental action)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;">
                    <h3 style="margin: 0; font-size: 1.2rem;">♻️ Recycling Rate</h3>
                    <h1 style="margin: 10px 0; font-size: 3rem; font-weight: bold;">{avg_rec_rate:.1f}%</h1>
                    <p style="margin: 0; opacity: 0.9;">Regional average</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_waste_pc = latest_data["waste_per_capita_kg"].mean()
                # Red gradient for waste (problem/concern)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); 
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
                # Purple gradient for champion (excellence/achievement)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 20px; border-radius: 10px; text-align: center; color: white;">
                    <h3 style="margin: 0; font-size: 1.2rem;">🥇 Champion</h3>
                    <h1 style="margin: 10px 0; font-size: 2rem; font-weight: bold;">{best_country}</h1>
                    <p style="margin: 0; opacity: 0.9;">{best_rate:.1f}% recycling</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                countries_above_30 = len(latest_data[latest_data["recycling_rate"] > 30])
                pct_above = (countries_above_30 / len(selected_countries)) * 100
                # Blue-green for target achievement (sustainable goal)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
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
            
            # Add stacked area chart for waste by sector (Europe)
            st.markdown("---")
            st.subheader("🔄 Waste Generation by Sector (Europe)")
            
            # Check if sector columns exist
            sector_cols = [col for col in df_waste_filt.columns if col.endswith("_tonnes") and col != "total_waste_tonnes"]
            
            if len(sector_cols) > 0:
                # Filter for European countries only
                eu_waste_data = df_waste_filt[df_waste_filt["country"].isin(selected_countries)]
                
                if len(eu_waste_data) > 0:
                    # Prepare data for stacked area chart
                    sector_data = eu_waste_data.groupby("year")[sector_cols].sum().reset_index()
                    
                    # Rename for better legend
                    sector_rename = {
                        "households_tonnes": "Households",
                        "construction_tonnes": "Construction",
                        "manufacturing_tonnes": "Manufacturing",
                        "services_tonnes": "Services"
                    }
                    
                    # Melt for plotting
                    sector_long = sector_data.melt(id_vars=["year"], value_vars=sector_cols, 
                                                   var_name="sector", value_name="tonnes")
                    sector_long["sector"] = sector_long["sector"].map(lambda x: sector_rename.get(x, x.replace("_tonnes", "").title()))
                    
                    # Semantic colors for sectors (reds/oranges for waste)
                    sector_colors = {
                        "Households": "#FF6B6B",      # Light red
                        "Construction": "#FFA500",    # Orange
                        "Manufacturing": "#FF8C42",   # Burnt orange
                        "Services": "#FFD93D"         # Yellow-orange
                    }
                    
                    fig_sector = px.area(
                        sector_long,
                        x="year",
                        y="tonnes",
                        color="sector",
                        title="European Waste Generation by Economic Sector Over Time",
                        labels={"year": "Year", "tonnes": "Waste (Tonnes)", "sector": "Sector"},
                        color_discrete_map=sector_colors
                    )
                    fig_sector.update_layout(
                        height=500,
                        hovermode="x unified",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_sector, use_container_width=True)
                    
                    st.markdown("""
                    <div class="insight-box">
                        <h4>📖 Interpretation Guide:</h4>
                        <ul>
                            <li><strong>Stacked area chart</strong> shows cumulative contribution of each sector</li>
                            <li><strong>Width of each color band</strong> = sector's contribution</li>
                            <li><strong>Total height</strong> = total waste generation across all selected countries</li>
                            <li><strong>Trends:</strong> Watch for expanding/shrinking sectors over time</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Sector breakdown data not available for selected European countries.")
            else:
                st.info("Sector breakdown data not available in the dataset.")
        else:
            st.warning("No complete data for this selection")
    
    else:  # North-South Comparison - show waste generation for ALL countries
        st.markdown("""
        <div class="insight-box">
            <h4>🌍 North-South Comparison: Waste Generation Analysis</h4>
            <p>Comparing waste production between European and African countries. 
            Note: Recycling data is only available for European countries.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if len(df_waste_filt) == 0:
            st.error("No data available")
            st.stop()
        
        latest_year = df_waste_filt["year"].max()
        latest = df_waste_filt[df_waste_filt["year"] == latest_year]
        latest = latest[latest["waste_per_capita_kg"].notna() & (latest["waste_per_capita_kg"] > 0)]
        
        if len(latest) == 0:
            st.error("No valid data for the selected period")
            st.stop()
        
        st.markdown(f"### 📅 Reference Year: **{int(latest_year)}**")
        st.markdown("---")
        
        # Split by region
        europe_countries = [c for c in selected_countries if c in europe_list]
        africa_countries = [c for c in selected_countries if c in africa_list]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🇪🇺 Europe")
            if europe_countries:
                eu_data = latest[latest["country"].isin(europe_countries)]
                if len(eu_data) > 0:
                    eu_avg = eu_data["waste_per_capita_kg"].mean()
                    eu_total = eu_data["total_waste_tonnes"].sum()
                    st.metric("Average per Capita", f"{eu_avg:.0f} kg/year")
                    st.metric("Total Waste", f"{eu_total/1_000_000:.1f} M tonnes")
                    st.metric("Countries", len(eu_data))
            else:
                st.info("No European countries selected")
        
        with col2:
            st.markdown("### 🌍 Africa")
            if africa_countries:
                af_data = latest[latest["country"].isin(africa_countries)]
                if len(af_data) > 0:
                    af_avg = af_data["waste_per_capita_kg"].mean()
                    af_total = af_data["total_waste_tonnes"].sum()
                    st.metric("Average per Capita", f"{af_avg:.0f} kg/year")
                    st.metric("Total Waste", f"{af_total/1_000_000:.1f} M tonnes")
                    st.metric("Countries", len(af_data))
            else:
                st.info("No African countries selected")
        
        st.markdown("---")
        
        # Add region column
        latest["region"] = latest["country"].apply(
            lambda x: "Europe" if x in europe_list else "Africa"
        )
        
        # Bar chart by region
        fig = px.bar(
            latest.sort_values("waste_per_capita_kg", ascending=True),
            x="waste_per_capita_kg",
            y="country",
            orientation="h",
            title=f"Waste Production per Capita - All Countries ({int(latest_year)})",
            labels={"waste_per_capita_kg": "kg/person/year", "country": "Country"},
            color="region",
            color_discrete_map={"Europe": "#4287f5", "Africa": "#f5a742"},
            text="waste_per_capita_kg"
        )
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        fig.update_layout(height=max(400, len(latest) * 30))
        st.plotly_chart(fig, use_container_width=True)

elif page == "Advanced Analytics" and "Europe" in region:
    st.header("🔬 Advanced Analytics")
    
    # Add explanation for advanced visualizations
    st.markdown("""
    <div class="insight-box">
        <h4>🔬 Why These Advanced Visualizations?</h4>
        <p><strong>Purpose:</strong> Uncover hidden patterns and relationships in data</p>
        <ul>
            <li><strong>Correlation heatmap:</strong> Shows which countries follow similar patterns (blue=positive, red=negative correlation)</li>
            <li><strong>Time series:</strong> Line charts ideal for tracking trends over time</li>
            <li><strong>Scatter plot quadrants:</strong> Categorize performance into 4 groups (champions vs. laggards)</li>
            <li><strong>Color psychology:</strong> Diverging scales (RdBu) for correlations, sequential (green/red) for performance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Use recycling data directly (already interpolated) and merge with waste data (also interpolated)
    valid_rec = df_rec_filt.dropna(subset=["recycling_rate"])
    valid_waste = df_waste_filt.dropna(subset=["waste_per_capita_kg"])
    valid_data = pd.merge(valid_rec, valid_waste[["country", "year", "waste_per_capita_kg"]], 
                         on=["country", "year"], how="inner")
    
    if len(valid_data) > 0:
        st.subheader("📊 Correlation Heatmap")
        
        pivot_rec = valid_data.pivot_table(
            values="recycling_rate",
            index="year",
            columns="country"
        )
        
        if pivot_rec.shape[1] > 1:
            corr_matrix = pivot_rec.corr()
            
            # Diverging color scale: blue=positive correlation, red=negative
            fig = px.imshow(
                corr_matrix,
                title="Country Recycling Rate Correlation Matrix (Blue=Similar Patterns)",
                labels=dict(color="Correlation"),
                color_continuous_scale="RdBu",
                aspect="auto"
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class="success-box">
                <h4>💡 Interpretation Guide</h4>
                <p><strong>Blue clusters:</strong> Countries with similar recycling trajectories (likely share policies or development levels)</p>
                <p><strong>Red values:</strong> Opposite trends (one improving while another declining)</p>
                <p><strong>Practical use:</strong> Identify best-practice sharing opportunities between correlated countries</p>
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
    
    # Add explanation for visualization choices
    st.markdown("""
    <div class="insight-box">
        <h4>🗺️ Why Choropleth Maps?</h4>
        <p><strong>Purpose:</strong> Visualize spatial patterns and geographic distribution</p>
        <ul>
            <li><strong>Choropleth maps:</strong> Best for comparing values across geographic regions</li>
            <li><strong>Color scales:</strong> 
                <ul>
                    <li>🟢 Green (RdYlGn): Recycling rates - red=low (bad), green=high (good)</li>
                    <li>🔴 Reds: Waste generation - darker red = more waste (problem intensity)</li>
                </ul>
            </li>
            <li><strong>Interactive hover:</strong> Detailed country-specific data on demand</li>
            <li><strong>Scope optimization:</strong> Regional focus for better readability</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if "Africa" in region and "Comparison" not in region:
        st.subheader("🌍 African Countries - Waste Production")
        
        latest_year = df_waste_filt["year"].max()
        latest_data = df_waste_filt[df_waste_filt["year"] == latest_year].copy()
        latest_data = latest_data[latest_data["waste_per_capita_kg"].notna()]
        
        if len(latest_data) > 0:
            # Semantic color: Reds for waste (darker = more waste = bigger problem)
            fig = px.choropleth(
                latest_data,
                locations="country_code",
                color="waste_per_capita_kg",
                hover_name="country",
                title=f"Waste Generation per Capita ({int(latest_year)}) - Red = Higher Waste",
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
    
    elif "Europe" in region and "Comparison" not in region:  # Europe only
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
    
    else:  # North-South Comparison
        st.markdown("""
        <div class="insight-box">
            <h4>🌍 Regional Comparison: Waste Production Maps</h4>
            <p>Comparing waste generation across European and African regions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        latest_year = df_waste_filt["year"].max()
        latest_all = df_waste_filt[df_waste_filt["year"] == latest_year].copy()
        latest_all = latest_all[latest_all["waste_per_capita_kg"].notna()]
        
        if len(latest_all) > 0:
            europe_countries_sel = [c for c in selected_countries if c in europe_list]
            africa_countries_sel = [c for c in selected_countries if c in africa_list]
            
            # Add region column for color coding
            latest_all["region"] = latest_all["country"].apply(
                lambda x: "Europe" if x in europe_list else "Africa"
            )
            
            # Single combined world map
            st.subheader(f"🗺️ Combined Waste Generation Map ({int(latest_year)})")
            
            fig_combined = px.choropleth(
                latest_all,
                locations="country_code",
                color="waste_per_capita_kg",
                hover_name="country",
                hover_data={"region": True, "waste_per_capita_kg": ":.0f", "country_code": False},
                title=f"Waste Generation per Capita - Europe & Africa ({int(latest_year)})",
                color_continuous_scale="RdYlGn_r",  # Red (high) to Green (low)
                labels={"waste_per_capita_kg": "kg/capita/year", "region": "Region"}
            )
            
            # Zoom to show both Europe and Africa
            fig_combined.update_geos(
                projection_type="natural earth",
                showcountries=True,
                showcoastlines=True,
                showland=True,
                landcolor="rgb(243, 243, 243)",
                coastlinecolor="rgb(204, 204, 204)",
                lataxis_range=[-40, 75],  # From South Africa to Northern Europe
                lonaxis_range=[-25, 55]   # From Atlantic to Eastern Europe/Middle East
            )
            
            fig_combined.update_layout(
                height=700,
                margin={"r":0,"t":50,"l":0,"b":0}
            )
            
            st.plotly_chart(fig_combined, use_container_width=True)
            
            # Regional statistics below the map
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🇪� Europe Statistics")
                if europe_countries_sel:
                    eu_data = latest_all[latest_all["country"].isin(europe_countries_sel)]
                    if len(eu_data) > 0:
                        st.metric("Countries", len(eu_data))
                        st.metric("Avg. Per Capita", f"{eu_data['waste_per_capita_kg'].mean():.0f} kg/year")
                        st.metric("Total Waste", f"{eu_data['total_waste_tonnes'].sum()/1_000_000:.1f} M tonnes")
                else:
                    st.info("No European countries selected")
            
            with col2:
                st.markdown("### 🌍 Africa Statistics")
                if africa_countries_sel:
                    af_data = latest_all[latest_all["country"].isin(africa_countries_sel)]
                    if len(af_data) > 0:
                        st.metric("Countries", len(af_data))
                        st.metric("Avg. Per Capita", f"{af_data['waste_per_capita_kg'].mean():.0f} kg/year")
                        st.metric("Total Waste", f"{af_data['total_waste_tonnes'].sum()/1_000_000:.1f} M tonnes")
                else:
                    st.info("No African countries selected")
            
            st.markdown("---")
            st.subheader("📍 Comparative Country Data")
            
            display_data = latest_all[["country", "region", "waste_per_capita_kg", "total_waste_tonnes", "population_millions"]].copy()
            display_data = display_data.sort_values("waste_per_capita_kg", ascending=False)
            
            st.dataframe(
                display_data.style.format({
                    "waste_per_capita_kg": "{:.0f} kg",
                    "total_waste_tonnes": "{:.0f}",
                    "population_millions": "{:.1f}M"
                }).background_gradient(subset=["waste_per_capita_kg"], cmap="YlOrRd"),
                use_container_width=True
            )
        else:
            st.warning("No geographic data available for selected period")

elif page == "Predictions & Risks":
    st.header("🔮 Predictions & Risk Analysis")
    
    st.markdown("""
    <div class="insight-box">
        <h4>🤖 Advanced Time Series Predictions</h4>
        <p><strong>ARIMA Model:</strong> Uses actual waste patterns (not just years) to predict future trends.</p>
        <ul>
            <li><strong>Autoregressive:</strong> Learns from past waste values (e.g., "if waste increased 5kg then decreased 2kg...")</li>
            <li><strong>Integrated:</strong> Handles trends and seasonality through differencing</li>
            <li><strong>Moving Average:</strong> Accounts for prediction errors</li>
            <li><strong>Rolling Window:</strong> Focus on recent years for better accuracy</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Forecasting parameters
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📈 Waste Production Forecasts")
    with col2:
        window_size = st.selectbox(
            "Training Window (years)",
            options=[3, 5, 7, 10],
            index=1,
            help="Number of recent years to use for prediction model. Smaller = follows recent trends, Larger = smoother predictions"
        )
    
    forecast_data = []
    for country in selected_countries:
        pred = forecast_waste(df_waste, country, years_ahead=5, window_size=window_size)
        if pred is not None:
            forecast_data.append(pred)
    
    if forecast_data:
        all_forecasts = pd.concat(forecast_data, ignore_index=True)
        
        # Display model usage statistics
        model_counts = all_forecasts.groupby('model_used')['country'].nunique()
        if len(model_counts) > 0:
            arima_count = model_counts.get('ARIMA', 0)
            lr_count = model_counts.get('Linear Regression (fallback)', 0)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div style="background: #4CAF50; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                    <h4 style="margin: 0;">🤖 ARIMA Model</h4>
                    <h2 style="margin: 10px 0;">{arima_count}</h2>
                    <p style="margin: 0;">countries (advanced)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div style="background: #FF9800; color: white; padding: 15px; border-radius: 10px; text-align: center;">
                    <h4 style="margin: 0;">📈 Linear Regression</h4>
                    <h2 style="margin: 10px 0;">{lr_count}</h2>
                    <p style="margin: 0;">countries (fallback)</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
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
        
        elif "Africa" in region:
            # Risk assessment for African countries (without recycling data)
            valid_data = df_waste_filt[df_waste_filt["waste_per_capita_kg"].notna() & 
                                       (df_waste_filt["waste_per_capita_kg"] > 0)]
            
            if len(valid_data) > 0:
                risk_data = []
                for country in selected_countries:
                    country_data = valid_data[valid_data["country"] == country].sort_values("year")
                    if len(country_data) >= 2:
                        latest_waste = country_data.iloc[-1]["waste_per_capita_kg"]
                        latest_total = country_data.iloc[-1]["total_waste_tonnes"] / 1_000_000  # In millions
                        
                        first_waste = country_data.iloc[0]["waste_per_capita_kg"]
                        last_waste = country_data.iloc[-1]["waste_per_capita_kg"]
                        years_span = country_data.iloc[-1]["year"] - country_data.iloc[0]["year"]
                        
                        if years_span > 0 and first_waste > 0:
                            growth_rate = ((last_waste / first_waste) ** (1/years_span) - 1) * 100
                        else:
                            growth_rate = 0
                        
                        risk_score = calculate_risk_score_africa(latest_waste, growth_rate, latest_total)
                        
                        risk_data.append({
                            "country": country,
                            "waste_per_capita": latest_waste,
                            "total_waste_millions": latest_total,
                            "growth_rate": growth_rate,
                            "risk_score": risk_score,
                            "risk_level": "High" if risk_score > 60 else "Medium" if risk_score > 30 else "Low"
                        })
                
                if risk_data:
                    risk_df = pd.DataFrame(risk_data).sort_values("risk_score", ascending=False)
                    
                    st.markdown("""
                    <div class="warning-box">
                        <h4>⚠️ Risk Assessment Model for African Countries</h4>
                        <p>This assessment considers: waste generation per capita, growth rate, and total volume.
                        Note: Recycling infrastructure data is not available for these countries.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
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
                            <p style="margin: 5px 0;">🗑️ Waste per Capita: {row["waste_per_capita"]:.0f} kg/year</p>
                            <p style="margin: 5px 0;">⚖️ Total Waste: {row["total_waste_millions"]:.2f} million tonnes</p>
                            <p style="margin: 5px 0;">📈 Growth Rate: {row["growth_rate"]:.2f}% per year</p>
                            <p style="margin: 5px 0;">⚠️ Limited recycling infrastructure</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Insufficient data for risk assessment. Need at least 2 years of data per country.")
            else:
                st.warning("No valid waste data available for risk assessment.")
        
        else:  # North-South Comparison
            st.markdown("""
            <div class="insight-box">
                <h4>🌍 Comparative Risk Assessment: Europe vs Africa</h4>
                <p>Different risk models are used due to data availability differences.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Europe risk scores
            europe_countries = [c for c in selected_countries if c in europe_list]
            africa_countries = [c for c in selected_countries if c in africa_list]
            
            all_risks = []
            
            if europe_countries:
                valid_eu = df_merged_filt[df_merged_filt["country"].isin(europe_countries)]
                valid_eu = valid_eu.dropna(subset=["recycling_rate", "waste_per_capita_kg"])
                
                for country in europe_countries:
                    country_data = valid_eu[valid_eu["country"] == country].sort_values("year")
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
                        
                        all_risks.append({
                            "country": country,
                            "region": "Europe",
                            "risk_score": risk_score,
                            "risk_level": "High" if risk_score > 60 else "Medium" if risk_score > 30 else "Low"
                        })
            
            if africa_countries:
                valid_af = df_waste_filt[df_waste_filt["country"].isin(africa_countries)]
                valid_af = valid_af[valid_af["waste_per_capita_kg"].notna() & 
                                   (valid_af["waste_per_capita_kg"] > 0)]
                
                for country in africa_countries:
                    country_data = valid_af[valid_af["country"] == country].sort_values("year")
                    if len(country_data) >= 2:
                        latest_waste = country_data.iloc[-1]["waste_per_capita_kg"]
                        latest_total = country_data.iloc[-1]["total_waste_tonnes"] / 1_000_000
                        
                        first_waste = country_data.iloc[0]["waste_per_capita_kg"]
                        last_waste = country_data.iloc[-1]["waste_per_capita_kg"]
                        years_span = country_data.iloc[-1]["year"] - country_data.iloc[0]["year"]
                        
                        if years_span > 0 and first_waste > 0:
                            growth_rate = ((last_waste / first_waste) ** (1/years_span) - 1) * 100
                        else:
                            growth_rate = 0
                        
                        risk_score = calculate_risk_score_africa(latest_waste, growth_rate, latest_total)
                        
                        all_risks.append({
                            "country": country,
                            "region": "Africa",
                            "risk_score": risk_score,
                            "risk_level": "High" if risk_score > 60 else "Medium" if risk_score > 30 else "Low"
                        })
            
            if all_risks:
                risk_df = pd.DataFrame(all_risks).sort_values("risk_score", ascending=False)
                
                fig = px.bar(
                    risk_df,
                    x="risk_score",
                    y="country",
                    orientation="h",
                    title="Comparative Environmental Risk Score",
                    labels={"risk_score": "Risk Score (0-100)", "country": "Country"},
                    color="region",
                    color_discrete_map={"Europe": "#4287f5", "Africa": "#f5a742"},
                    text="risk_score"
                )
                fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
                fig.update_layout(height=max(400, len(risk_df) * 40))
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🇪🇺 Europe")
                    eu_risks = risk_df[risk_df["region"] == "Europe"]
                    if len(eu_risks) > 0:
                        avg_risk = eu_risks["risk_score"].mean()
                        st.metric("Average Risk Score", f"{avg_risk:.0f}/100")
                        st.dataframe(eu_risks[["country", "risk_score", "risk_level"]], use_container_width=True)
                    else:
                        st.info("No European countries selected")
                
                with col2:
                    st.markdown("### 🌍 Africa")
                    af_risks = risk_df[risk_df["region"] == "Africa"]
                    if len(af_risks) > 0:
                        avg_risk = af_risks["risk_score"].mean()
                        st.metric("Average Risk Score", f"{avg_risk:.0f}/100")
                        st.dataframe(af_risks[["country", "risk_score", "risk_level"]], use_container_width=True)
                    else:
                        st.info("No African countries selected")
            else:
                st.warning("Insufficient data for comparative risk assessment.")
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
    
    if "Africa" in region and "Comparison" not in region:
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
    
    elif "Europe" in region and "Comparison" not in region:  # Europe only
        # Use recycling data directly (already interpolated) and merge with waste data (also interpolated)
        valid_rec = df_rec_filt.dropna(subset=["recycling_rate"])
        valid_waste = df_waste_filt.dropna(subset=["waste_per_capita_kg"])
        valid = pd.merge(valid_rec, valid_waste[["country", "year", "waste_per_capita_kg"]], 
                        on=["country", "year"], how="inner")
        
        if len(valid) > 0:
            best_yr = valid.groupby("year")["country"].count().idxmax()
            ranking = valid[valid["year"] == best_yr]
            ranking = ranking[["country", "recycling_rate", "waste_per_capita_kg"]].copy()
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
    
    else:  # North-South Comparison
        st.markdown("""
        <div class="insight-box">
            <h4>🌍 North-South Comparison Rankings</h4>
            <p>Ranking all countries by waste production (kg per capita). 
            Europe also shows recycling rates where available.</p>
        </div>
        """, unsafe_allow_html=True)
        
        latest_yr = df_waste_filt["year"].max()
        latest_all = df_waste_filt[df_waste_filt["year"] == latest_yr].copy()
        latest_all = latest_all[latest_all["waste_per_capita_kg"].notna()]
        
        if len(latest_all) > 0:
            # Add region column
            latest_all["region"] = latest_all["country"].apply(
                lambda x: "Europe" if x in europe_list else "Africa"
            )
            
            # Merge with recycling data for Europe (if available for this year)
            rec_latest = df_rec_filt[df_rec_filt["year"] == df_rec_filt["year"].max()]
            if len(rec_latest) > 0:
                latest_all = latest_all.merge(
                    rec_latest[["country", "recycling_rate"]],
                    on="country",
                    how="left"
                )
            
            # Overall ranking by waste production
            st.subheader(f"🌍 Combined Ranking by Waste Production ({int(latest_yr)})")
            ranking_all = latest_all[["country", "region", "waste_per_capita_kg", "recycling_rate", "total_waste_tonnes"]].copy()
            ranking_all = ranking_all.sort_values("waste_per_capita_kg", ascending=False)
            
            st.dataframe(
                ranking_all.style.format({
                    "waste_per_capita_kg": "{:.0f} kg",
                    "recycling_rate": "{:.1f}%",
                    "total_waste_tonnes": "{:.0f}"
                }).background_gradient(subset=["waste_per_capita_kg"], cmap="YlOrRd"),
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Regional sub-rankings
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🇪🇺 Europe - Top Performers")
                eu_data = ranking_all[ranking_all["region"] == "Europe"].copy()
                if len(eu_data) > 0:
                    # Rank by recycling rate (best recyclers)
                    eu_ranked = eu_data.dropna(subset=["recycling_rate"]).sort_values("recycling_rate", ascending=False)
                    if len(eu_ranked) > 0:
                        st.markdown("**Best Recyclers:**")
                        medals = ["🥇", "🥈", "🥉"]
                        for i in range(min(3, len(eu_ranked))):
                            row = eu_ranked.iloc[i]
                            st.success(f"{medals[i]} **{row['country']}** - {row['recycling_rate']:.1f}%")
                    
                    st.markdown("**Lowest Waste Producers:**")
                    eu_low = eu_data.sort_values("waste_per_capita_kg").head(3)
                    for i, (_, row) in enumerate(eu_low.iterrows()):
                        st.info(f"{i+1}. **{row['country']}** - {row['waste_per_capita_kg']:.0f} kg/yr")
            
            with col2:
                st.subheader("🌍 Africa - Top Performers")
                af_data = ranking_all[ranking_all["region"] == "Africa"].copy()
                if len(af_data) > 0:
                    st.markdown("**Lowest Waste Producers:**")
                    af_low = af_data.sort_values("waste_per_capita_kg").head(3)
                    medals = ["🥇", "🥈", "🥉"]
                    for i, (_, row) in enumerate(af_low.iterrows()):
                        st.success(f"{medals[i]} **{row['country']}** - {row['waste_per_capita_kg']:.0f} kg/yr")
                    
                    st.markdown("**Highest Producers (need attention):**")
                    af_high = af_data.sort_values("waste_per_capita_kg", ascending=False).head(3)
                    for i, (_, row) in enumerate(af_high.iterrows()):
                        st.warning(f"{i+1}. **{row['country']}** - {row['waste_per_capita_kg']:.0f} kg/yr")

elif page == "Waste Production":
    st.header("📦 Waste Production - Detailed Analysis")
    
    # Add explanation for why this page exists
    st.markdown("""
    <div class="insight-box">
        <h4>📊 Why This Visualization?</h4>
        <p><strong>Purpose:</strong> Understand waste composition and trends by sector</p>
        <ul>
            <li><strong>Bar chart:</strong> Easy comparison of total volumes across countries</li>
            <li><strong>Stacked area chart:</strong> Reveals sector contribution trends over time</li>
            <li><strong>Line chart:</strong> Shows individual country trajectories</li>
            <li><strong>Color scheme:</strong> Reds/oranges for waste (red = danger/waste)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if len(df_waste_filt) == 0:
        st.error("No data available")
        st.stop()
    
    st.subheader("📊 Total Production by Country")
    
    latest_year = df_waste_filt["year"].max()
    latest = df_waste_filt[df_waste_filt["year"] == latest_year]
    
    # Improved color scheme: Red gradient for waste (red = danger)
    fig1 = px.bar(
        latest.sort_values("total_waste_tonnes", ascending=True),
        x="total_waste_tonnes",
        y="country",
        orientation="h",
        title=f"Total Waste Production ({int(latest_year)})",
        labels={"total_waste_tonnes": "Tonnes", "country": "Country"},
        color="total_waste_tonnes",
        color_continuous_scale="Reds",  # Red for waste (semantic: danger/problem)
        text="total_waste_tonnes"
    )
    fig1.update_traces(texttemplate="%{text:.2s}", textposition="outside")
    fig1.update_layout(height=max(400, len(latest) * 25))
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🔄 Waste Generation by Sector (Stacked Area)")
    
    # Check if sector columns exist
    sector_cols = [col for col in df_waste_filt.columns if col.endswith("_tonnes") and col != "total_waste_tonnes"]
    
    if len(sector_cols) > 0:
        # Prepare data for stacked area chart
        sector_data = df_waste_filt.groupby("year")[sector_cols].sum().reset_index()
        
        # Rename for better legend
        sector_rename = {
            "households_tonnes": "Households",
            "construction_tonnes": "Construction",
            "manufacturing_tonnes": "Manufacturing",
            "services_tonnes": "Services"
        }
        
        # Melt for plotting
        sector_long = sector_data.melt(id_vars=["year"], value_vars=sector_cols, 
                                       var_name="sector", value_name="tonnes")
        sector_long["sector"] = sector_long["sector"].map(lambda x: sector_rename.get(x, x.replace("_tonnes", "").title()))
        
        # Semantic colors for sectors
        sector_colors = {
            "Households": "#FF6B6B",      # Light red
            "Construction": "#FFA500",    # Orange
            "Manufacturing": "#FF8C42",   # Burnt orange
            "Services": "#FFD93D"         # Yellow-orange
        }
        
        fig_sector = px.area(
            sector_long,
            x="year",
            y="tonnes",
            color="sector",
            title="Waste Generation by Economic Sector Over Time",
            labels={"year": "Year", "tonnes": "Waste (Tonnes)", "sector": "Sector"},
            color_discrete_map=sector_colors
        )
        fig_sector.update_layout(
            height=500,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_sector, use_container_width=True)
        
        st.markdown("""
        **📖 Interpretation Guide:**
        - **Stacked area chart** shows cumulative contribution of each sector
        - **Width of each color band** = sector's contribution
        - **Total height** = total waste generation
        - **Trends:** Watch for expanding/shrinking sectors over time
        """)
    else:
        st.info("Sector breakdown data not available for selected countries.")
    
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
