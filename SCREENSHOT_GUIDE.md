# 📸 Dashboard Screenshot Guide

## Directory Setup
Create a folder named `screenshots` in your project directory:
```
DataVisTp1/
├── screenshots/          ← Create this folder
│   ├── 01_overview_europe.png
│   ├── 02_overview_comparison.png
│   └── ...
├── app.py
└── dashboard_report.tex
```

## Screenshot Instructions

### 🎯 How to Take Screenshots
1. Run your Streamlit dashboard: `streamlit run app.py`
2. Use Windows Snipping Tool (Win + Shift + S) or Snip & Sketch
3. Capture the main content area (exclude browser chrome if possible)
4. Save with the exact filenames listed below
5. Recommended resolution: 1920x1080 or 1600x900
6. Format: PNG (for best quality)

---

## 📋 Required Screenshots (12 Total)

### **Section 1: Overview & KPIs**

#### **01_overview_europe.png**
- **Region**: Select "Europe (with recycling)"
- **Countries**: Select 4-6 European countries (e.g., France, Germany, Italy, Spain)
- **Page**: Overview & KPIs
- **Year Range**: 2010-2014
- **What to capture**: 
  - The 4 gradient KPI cards (Recycling Rate, Production, Champion, Target 30%)
  - Top 5 recycling and Top 5 to improve lists
  - The scatter plot showing Recycling vs Production

#### **02_overview_comparison.png**
- **Region**: Select "North-South Comparison"
- **Countries**: Select mix of European (France, Germany) and African (Algeria, Morocco, Egypt)
- **Page**: Overview & KPIs
- **Year Range**: 2010-2014
- **What to capture**:
  - Europe vs Africa regional metrics (2 columns)
  - Combined bar chart showing all countries colored by region

---

### **Section 2: Geographic Analysis**

#### **03_geographic_europe.png**
- **Region**: Europe (with recycling)
- **Countries**: Select 8-10 European countries
- **Page**: Geographic Analysis
- **Year Range**: 2012-2014
- **What to capture**: 
  - The European choropleth map showing recycling rates
  - Make sure color scale is visible (green = high recycling, red = low)

#### **04_geographic_africa.png**
- **Region**: Africa (generation)
- **Countries**: Select all 10 African countries
- **Page**: Geographic Analysis
- **Year Range**: 2014-2020
- **What to capture**:
  - The African choropleth map showing waste per capita
  - Color scale visible (darker red = higher waste)

#### **05_geographic_combined.png**
- **Region**: North-South Comparison
- **Countries**: Mix of 5 European + 5 African countries
- **Page**: Geographic Analysis
- **Year Range**: 2010-2014
- **What to capture**:
  - The combined world map showing both continents
  - Regional statistics boxes below the map (2 columns: Europe | Africa)

---

### **Section 3: Advanced Analytics & Trends**

#### **06_advanced_analytics.png**
- **Region**: Europe (with recycling)
- **Countries**: Select 6-8 European countries
- **Page**: Advanced Analytics
- **Year Range**: 2000-2014
- **What to capture**:
  - The correlation heatmap (should show country correlations)
  - OR the performance quadrant scatter plot
  - Make sure axes labels are visible

#### **07_temporal_trends.png**
- **Region**: Europe (with recycling)
- **Countries**: Select 4-5 European countries with different performance levels
- **Page**: Temporal Trends
- **Year Range**: 2000-2015
- **What to capture**:
  - Line chart showing recycling rate evolution over time
  - Multiple colored lines (one per country)
  - The 30% target red dashed line should be visible

---

### **Section 4: Predictions & Forecasting**

#### **08_predictions_europe.png**
- **Region**: Europe (with recycling)
- **Countries**: Select 3-4 European countries
- **Page**: Predictions & Risks
- **Year Range**: 2005-2014
- **Window Size**: 5 years
- **What to capture**:
  - The forecast chart showing historical data + 5-year predictions
  - Different colored lines for different countries
  - Make sure both historical and predicted segments are visible

#### **09_predictions_africa.png**
- **Region**: Africa (generation)
- **Countries**: Select 3-4 African countries
- **Page**: Predictions & Risks
- **Year Range**: 2010-2020
- **Window Size**: 5 years
- **What to capture**:
  - Similar forecast chart for African countries
  - Show the upward trend predictions

---

### **Section 5: Risk Assessment**

#### **10_risk_assessment_europe.png**
- **Region**: Europe (with recycling)
- **Countries**: Select 6-8 European countries with varied performance
- **Page**: Predictions & Risks (scroll down to Risk Assessment section)
- **Year Range**: 2010-2014
- **What to capture**:
  - The horizontal bar chart showing risk scores (0-100)
  - Color coding: green (low risk), yellow (medium), red (high)
  - Risk factor cards below the chart

#### **11_risk_assessment_comparison.png**
- **Region**: North-South Comparison
- **Countries**: Mix of 4 European + 4 African countries
- **Page**: Predictions & Risks (scroll to Risk Assessment)
- **Year Range**: 2010-2014
- **What to capture**:
  - The comparative risk assessment showing both regions
  - Regional average risk scores
  - Side-by-side comparison charts or tables

#### **12_rankings.png**
- **Region**: North-South Comparison (or Europe)
- **Countries**: 6-8 countries
- **Page**: Rankings
- **Year Range**: 2012-2014
- **What to capture**:
  - The ranking table with countries sorted by performance
  - Podium section showing top 3 performers
  - Background gradient colors on the table

---

## 🎨 Screenshot Quality Tips

### ✅ Do:
- Use full browser width (at least 1400px)
- Ensure all text is readable
- Capture legends and color scales
- Include chart titles
- Make sure gradients and colors are visible
- Use consistent zoom level across screenshots

### ❌ Don't:
- Include browser address bar or tabs
- Crop chart titles or legends
- Use dark mode (if it affects readability)
- Capture while data is loading
- Include scrollbars if possible

---

## 🔧 After Taking Screenshots

1. Save all 12 files in `screenshots/` folder with exact names listed above
2. Verify all images are PNG format
3. Check that filenames match exactly (case-sensitive!)
4. Recompile LaTeX document:
   ```bash
   pdflatex dashboard_report.tex
   pdflatex dashboard_report.tex  # Run twice for proper figure numbering
   ```
5. Review the PDF to ensure all images appear correctly

---

## 📏 Recommended Image Sizes

- **Width**: 1600-1920 pixels
- **Height**: 900-1200 pixels (varies by content)
- **Format**: PNG
- **Color depth**: 24-bit RGB
- **File size**: Keep under 2MB per image (compress if needed)

---

## 🆘 Troubleshooting

**Problem**: "File not found" error in LaTeX
- **Solution**: Check that folder is named exactly `screenshots` (lowercase, plural)
- Verify filename matches exactly (check for spaces or typos)

**Problem**: Images too large in PDF
- **Solution**: Adjust the width parameter in .tex file
- Change `width=0.95\textwidth` to `width=0.8\textwidth`

**Problem**: Images appear blurry
- **Solution**: Take screenshots at higher resolution
- Use PNG format instead of JPG
- Don't compress images too much

---

## ✅ Checklist

Before compiling final report:
- [ ] Created `screenshots/` folder
- [ ] Taken all 12 screenshots
- [ ] Verified all filenames match exactly
- [ ] All images are PNG format
- [ ] Images are readable and high quality
- [ ] Compiled LaTeX twice
- [ ] Reviewed PDF output

---

**Note**: You can also use Streamlit's built-in screenshot feature or browser extensions like "Full Page Screen Capture" for better quality screenshots!
