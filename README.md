# ♻️ Environmental Dashboard - Waste Management Analysis

Interactive Streamlit dashboard for comparative analysis of waste management practices between European and African countries.

## 📊 Project Overview

This project provides comprehensive waste management analysis across 49 countries (27 European + 22 African), focusing on:
- Recycling rates and circular economy progress (Europe)
- Waste generation trends and per capita metrics
- Waste by economic sector (households, construction, manufacturing, services)
- Machine learning forecasting (ARIMA time series models)
- Environmental risk assessment
- North-South comparative analysis

**Deliverables:**
- ✅ Interactive Streamlit dashboard with 6+ pages (`app.py`)
- ✅ ARIMA-based waste forecasting (ML predictions)
- ✅ Rule-based environmental risk assessment
- ✅ LaTeX report with visualization design rationale (`dashboard_report.tex`)
- ✅ 49-country dataset with interpolation (27 Europe, 22 Africa)
- ✅ Semantic color scheme and accessibility features

## 🗂️ Project Structure

```
DataVisTp1/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── data/                           # Cleaned datasets (generated)
│   ├── clean_waste_generation.csv
│   ├── clean_recycling_rate.csv
│   ├── clean_waste_by_type_algeria.csv
│   └── algeria_waste_with_yoy.csv
│
├── notebooks/                      # Data preparation
│   └── data_prep.ipynb            # Jupyter notebook for data cleaning
│
├── assets/                         # Images, logos (optional)
│
├── total-waste-generation/         # Raw data
│   ├── total-waste-generation.csv
│   ├── total-waste-generation.metadata.json
│   └── readme.md
│
└── municipal-waste-recycling-rate/ # Raw data
    ├── municipal-waste-recycling-rate.csv
    ├── municipal-waste-recycling-rate.metadata.json
    └── readme.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download this repository**

2. **Navigate to the project directory**
   ```powershell
   cd c:\Users\LENOVO\Desktop\DataVisTp1
   ```

3. **Install required packages**
   ```powershell
   pip install -r requirements.txt
   ```

### Data Preparation (Optional)

The dashboard can work with raw data directly, but for better performance, run the data preparation notebook first:

1. **Open Jupyter Notebook**
   ```powershell
   jupyter notebook
   ```

2. **Navigate to `notebooks/data_prep.ipynb`**

3. **Run all cells** to generate cleaned datasets in the `data/` folder

### Running the Dashboard

```powershell
streamlit run app.py
```

The dashboard will open automatically in your default web browser at `http://localhost:8501`

## 📊 Dashboard Features

### 1. Overview & KPIs
- **Region Selection**: Europe (with recycling) | Africa (generation only) | North-South Comparison
- **Semantic KPI Cards**: Green (recycling), Red (waste), Purple (champions), Blue (targets)
- **Top 5 Rankings**: Best recyclers and lowest waste producers
- **Stacked Area Charts**: Waste by sector over time (households, construction, manufacturing, services)
- **Performance Scatter Plot**: Recycling rate vs. waste per capita

### 2. Geographic Analysis
- **Choropleth Maps**: Europe (recycling rates), Africa (waste per capita), Combined world view
- **Interactive Hover**: Country-specific data on demand
- **Color Scales**: RdYlGn for recycling (green=good), Reds for waste (red=danger)
- **Optimized Zoom**: Natural earth projection covering both continents

### 3. Temporal Trends
- **Multi-country Line Charts**: Recycling and waste evolution over time
- **30% Target Line**: EU recycling goal reference
- **Interpolated Annual Data**: Linear interpolation fills biennial gaps

### 4. Advanced Analytics (Europe)
- **Correlation Heatmap**: Inter-country recycling pattern similarities (RdBu diverging scale)
- **Performance Quadrants**: 4-category classification (high/low recycling × high/low waste)
- **Trend Analysis**: Dual-axis charts with regional averages

### 5. Predictions & Risks
- **ARIMA Forecasting**: 5-year waste predictions using autoregressive time series models
- **Fallback Indicator**: Visual badges showing ARIMA vs. Linear Regression usage
- **Configurable Window**: 3, 5, 7, or 10-year rolling windows
- **Risk Assessment**: Rule-based scoring (0-100) with color-coded priority levels
- **Dual Risk Models**: Europe (recycling-focused) vs. Africa (growth-focused)

### 6. Waste Production
- **Sector Breakdown**: Stacked area charts for 4 economic sectors
- **Bar Charts**: Total production by country (sorted)
- **Evolution Lines**: Individual country trajectories
- **Explanation Boxes**: "Why This Visualization?" guides on every page

### 7. Rankings
- **Sortable Tables**: Recycling rates and waste per capita
- **Gradient Backgrounds**: Visual encoding of performance
- **Podium Display**: Medal system for top 3 countries
- **Regional Comparisons**: Side-by-side Europe vs. Africa

## 📈 Key Indicators

The dashboard tracks and visualizes these indicators:

1. **Recycling Rate** (%) - Europe only, OECD data
2. **Waste per Capita** (kg/person/year) - Universal metric
3. **Total Waste Generation** (tonnes) - Absolute volumes
4. **Growth Rate** (%/year) - Compound annual growth
5. **Environmental Risk Score** (0-100) - Rule-based composite
6. **Waste by Sector** (tonnes):
   - Households
   - Construction
   - Manufacturing
   - Services
7. **Predicted Waste** (5-year ARIMA forecasts)
8. **Target Achievement** - Countries above 30% recycling (Europe)

## 📁 Data Sources

- **Total Waste Generation**: UN Environment Programme (132 countries globally)
- **Recycling Rates**: OECD - Municipal Waste Recycling Rate (38 European countries)
- **Population**: Embedded in dashboard for per capita calculations

**Coverage:**
- **Years**: 1990-2021 (biennial data, interpolated to annual)
- **European countries**: 27 (France, Germany, Italy, Spain, Belgium, Netherlands, Austria, Denmark, Sweden, Finland, Norway, Switzerland, Poland, Portugal, Greece, Ireland, Czechia, UK, Luxembourg, Slovenia, Slovakia, Estonia, Hungary, Iceland, Latvia, Lithuania, Turkey)
- **African countries**: 22 (Algeria, Egypt, Morocco, Tunisia, South Africa, Kenya, Ghana, Botswana, Mauritius, Benin, Burkina Faso, Burundi, Cape Verde, Guinea, Lesotho, Madagascar, Niger, Sudan, Tanzania, Togo, Zambia, Zimbabwe)
- **Last Updated**: November 2025

## 🔧 Tech Stack

- **Streamlit** 1.28.0 - Web application framework
- **Pandas** 2.1.1 - Data manipulation and time series
- **Plotly** 5.17.0 - Interactive visualizations
- **scikit-learn** 1.5.1 - Machine learning (Linear Regression fallback)
- **statsmodels** - ARIMA time series forecasting
- **NumPy** 1.24.3 - Numerical computations
- **Python** 3.8+ - Programming language

## 📝 Report and Presentation Guidelines

### PDF Report (3-5 pages)

**Recommended Structure:**

1. **Title Page**
   - Project title
   - Author(s)
   - Date
   - Institution

2. **Introduction** (½ page)
   - Context: Waste management challenges in Algeria
   - Objectives of the analysis
   - Problem statement

3. **Data & Methodology** (1 page)
   - Data sources and citations
   - Year coverage and geographic scope
   - Cleaning steps performed
   - Limitations and data quality notes
   - List of 5-8 indicators selected

4. **Visualizations & Analysis** (2 pages)
   - 4-6 key charts from the dashboard (screenshots)
   - Brief interpretation for each visual
   - Highlight trends, patterns, and anomalies
   - Comparative insights

5. **Findings & Recommendations** (1 page)
   - 4-6 main findings (bullet points)
   - Actionable recommendations:
     - Increase source separation
     - Improve data collection
     - Develop recycling infrastructure
     - Scale composting programs
     - Regional priorities

6. **Appendix** (optional)
   - Data dictionary
   - Additional tables
   - Code references

**Tools for PDF Generation:**
- Microsoft Word → Export as PDF
- LaTeX (Overleaf)
- Google Docs
- Jupyter Notebook → PDF export
- Python: `reportlab`, `weasyprint`, or `matplotlib` for charts

### Presentation Slides (3-6 slides)

**Recommended Structure:**

1. **Slide 1: Title**
   - Project title
   - Your name
   - Date

2. **Slide 2: Context & Objectives**
   - Why waste management matters
   - Data sources
   - Key questions

3. **Slide 3: Key Findings (Visual)**
   - 2-3 impactful charts
   - Main trend (waste growth)
   - Per capita metrics

4. **Slide 4: Composition Analysis**
   - Pie/donut chart of waste by sector
   - Key insight about household waste dominance

5. **Slide 5: International Comparison** (optional)
   - How Algeria compares to neighbors
   - Chart showing multi-country trends

6. **Slide 6: Recommendations**
   - 3-5 key recommendations (bullets)
   - Call to action
   - Thank you

**Tools:**
- Microsoft PowerPoint
- Google Slides
- Python: `python-pptx` library (included in requirements.txt)

## 📊 Sample Code for Automated Reporting

### Save Charts as Images (for report)

```python
import plotly.io as pio

# After creating a plotly figure
fig = px.line(...)  # your chart

# Save as PNG
pio.write_image(fig, "assets/chart_waste_trend.png", width=1200, height=600)
```

### Generate PowerPoint Programmatically

```python
from pptx import Presentation
from pptx.util import Inches

# Create presentation
prs = Presentation()

# Add title slide
title_slide = prs.slides.add_slide(prs.slide_layouts[0])
title = title_slide.shapes.title
title.text = "Waste Management Dashboard - Algeria"

# Add content slide
content_slide = prs.slides.add_slide(prs.slide_layouts[1])
title = content_slide.shapes.title
title.text = "Key Findings"

# Add image
img_path = "assets/chart_waste_trend.png"
content_slide.shapes.add_picture(img_path, Inches(1), Inches(2), width=Inches(8))

# Save
prs.save("slides.pptx")
```

## 🎯 Grading Criteria (as per assignment)

The project addresses three main evaluation areas:

### 1. Données et Indicateurs (5 points)
- ✅ Multiple data sources documented
- ✅ 5-8 key indicators selected and justified
- ✅ Data quality and limitations addressed
- ✅ Cleaning methodology documented

### 2. Dashboard Design & Interactivity (5 points)
- ✅ Multi-page/section layout
- ✅ Interactive filters (year slider, country selector)
- ✅ Clear visualizations with titles, legends, units
- ✅ Tooltips and hover information
- ✅ Export functionality

### 3. Analysis & Communication (5 points)
- ✅ Clear findings documented
- ✅ Actionable recommendations
- ✅ Professional report structure
- ✅ Concise presentation slides
- ✅ Proper citations and sources

## 📅 Timeline (6 weeks suggested)

- **Week 1**: Dataset acquisition & cleaning ✅
- **Week 2**: Data model + base visualizations ✅
- **Week 3**: Composition charts + comparisons ✅
- **Week 4**: Interactivity, filters, polish ✅
- **Week 5**: Write report.pdf and prepare slides 🔄
- **Week 6**: Final review, testing, submission 📦

## 🐛 Troubleshooting

### Data Not Loading
- Ensure you're running the app from the project root directory
- Check that raw data folders exist: `total-waste-generation/` and `municipal-waste-recycling-rate/`
- Run the data preparation notebook first to generate cleaned files

### Module Not Found
```powershell
pip install -r requirements.txt
```

### Port Already in Use
```powershell
streamlit run app.py --server.port 8502
```

### Charts Not Displaying
- Clear Streamlit cache: Click the hamburger menu → "Clear cache"
- Check browser console for JavaScript errors
- Try a different browser (Chrome recommended)

## 📚 Additional Resources

- **Streamlit Documentation**: https://docs.streamlit.io
- **Plotly Documentation**: https://plotly.com/python/
- **Our World in Data**: https://ourworldindata.org
- **OECD Environment Statistics**: https://stats.oecd.org

## 🤝 Contributing

This is an educational project. Suggestions for improvements:
- Add wilaya-level geographic data
- Integrate real-time data APIs
- Add predictive models for waste generation
- Include economic indicators (GDP correlation)
- Expand recycling infrastructure analysis

## 📄 License

Educational project - Data sources have their own licenses:
- Our World in Data: CC BY 4.0
- OECD: Check specific dataset terms

## 👤 Author

Data Visualization Project - October 2025

## 🙏 Acknowledgments

- Our World in Data for providing accessible environmental data
- UN Environment Programme for waste generation statistics
- OECD for municipal waste management indicators
- Streamlit team for the excellent dashboard framework

---

**Last Updated**: October 27, 2025

For questions or issues, please refer to the documentation or contact your instructor.
