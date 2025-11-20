# 🔧 TROUBLESHOOTING GUIDE

Common issues and their solutions for the Waste Management Dashboard.

---

## ✅ Dashboard Fixed - Now Ready to Run!

The dashboard has been updated to handle both raw and cleaned data gracefully. You can now run it immediately!

---

## 🚀 QUICK FIX - Start Here

### Error: "KeyError: 'yoy_change_percent' not in index"

**Status:** ✅ FIXED

**Solution:** Just run the dashboard now:
```powershell
streamlit run app.py
```

The dashboard will work with raw data. You'll see a blue info box suggesting to run the data prep notebook for advanced features, but everything essential works!

---

## 📊 Dashboard Status

### ✅ Works Immediately With Raw Data
- Total waste trends
- Per capita calculations (basic)
- Composition charts
- Country comparisons
- All visualizations

### 🔄 Enhanced After Running Data Prep Notebook
- Year-over-year change charts
- Advanced metrics
- Optimized performance
- All cleaned datasets

---

## 🐛 Common Issues & Solutions

### Issue 1: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```powershell
pip install -r requirements.txt
```

If that fails, install individually:
```powershell
pip install streamlit pandas plotly numpy
```

---

### Issue 2: Dashboard Won't Start
```
streamlit: command not found
```

**Solution A - Use Python module:**
```powershell
python -m streamlit run app.py
```

**Solution B - Check installation:**
```powershell
pip show streamlit
```

If not installed:
```powershell
pip install streamlit
```

---

### Issue 3: Port Already in Use
```
OSError: [Errno 98] Address already in use
```

**Solution - Use different port:**
```powershell
streamlit run app.py --server.port 8502
```

---

### Issue 4: Charts Not Displaying

**Symptoms:** Blank spaces where charts should be

**Solutions:**
1. **Clear Streamlit cache:**
   - Click hamburger menu (☰) in dashboard
   - Select "Clear cache"
   - Refresh page

2. **Check browser console:**
   - Press F12 in browser
   - Look for JavaScript errors
   - Try different browser (Chrome recommended)

3. **Verify data files exist:**
   ```powershell
   dir total-waste-generation\total-waste-generation.csv
   dir municipal-waste-recycling-rate\municipal-waste-recycling-rate.csv
   ```

---

### Issue 5: Jupyter Notebook Won't Start
```
'jupyter' is not recognized as an internal or external command
```

**Solution:**
```powershell
pip install jupyter notebook
```

Then run:
```powershell
jupyter notebook
```

---

### Issue 6: Kaleido Error (Chart Export)
```
ValueError: The kaleido package is required to export images
```

**Solution:**
```powershell
pip install kaleido
```

For troublesome installations:
```powershell
pip install kaleido --upgrade
```

---

### Issue 7: File Not Found Errors

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solutions:**
1. **Verify you're in the correct directory:**
   ```powershell
   cd C:\Users\LENOVO\Desktop\DataVisTp1
   pwd  # Should show DataVisTp1
   ```

2. **Check file exists:**
   ```powershell
   dir app.py
   dir requirements.txt
   ```

3. **Verify folder structure:**
   ```powershell
   tree /F
   ```

---

### Issue 8: Permission Denied

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. **Close any open files** (Excel, Jupyter, etc.)
2. **Run PowerShell as Administrator** (right-click → Run as administrator)
3. **Check file/folder permissions**

---

### Issue 9: Data Not Loading in Dashboard

**Symptoms:** Error message about data loading

**Solutions:**
1. **Verify data files are in correct location:**
   ```
   DataVisTp1/
   ├── total-waste-generation/
   │   └── total-waste-generation.csv  ← Must exist
   └── municipal-waste-recycling-rate/
       └── municipal-waste-recycling-rate.csv  ← Must exist
   ```

2. **Check file encoding:** Files should be UTF-8
3. **Verify CSV format:** Open in text editor to check structure

---

### Issue 10: Slow Performance

**Solutions:**
1. **Run data prep notebook** to generate cleaned files
2. **Close other applications**
3. **Use smaller year range** in filters
4. **Clear browser cache**

---

## 🔍 Diagnostic Steps

If you encounter any other issue:

### Step 1: Check Python Version
```powershell
python --version
```
Should be 3.8 or higher.

### Step 2: Verify Installation
```powershell
pip list | findstr "streamlit pandas plotly"
```
All should be listed.

### Step 3: Test Data Loading
```powershell
python -c "import pandas as pd; df = pd.read_csv('total-waste-generation/total-waste-generation.csv'); print(df.head())"
```

### Step 4: Check Streamlit
```powershell
streamlit --version
```

### Step 5: Review Error Messages
- Read the full error traceback
- Note the file and line number
- Check what the error says

---

## 📱 Platform-Specific Issues

### Windows PowerShell

**Issue:** Scripts disabled
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Anaconda Users

If using Anaconda, activate environment first:
```powershell
conda activate base
pip install -r requirements.txt
streamlit run app.py
```

---

## 🆘 Still Having Issues?

### Checklist
- [ ] Python 3.8+ installed
- [ ] In correct directory (DataVisTp1)
- [ ] All dependencies installed
- [ ] Data files present
- [ ] No files open in other programs
- [ ] Internet connection (for first run)

### Nuclear Option (Fresh Start)
```powershell
# 1. Create new virtual environment
python -m venv venv_dashboard

# 2. Activate it
.\venv_dashboard\Scripts\Activate.ps1

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Run dashboard
streamlit run app.py
```

---

## 📊 Verification Commands

Test that everything works:

```powershell
# Navigate to project
cd C:\Users\LENOVO\Desktop\DataVisTp1

# Verify files
dir app.py
dir requirements.txt

# Test Python
python --version

# Test imports
python -c "import streamlit, pandas, plotly; print('✓ All imports successful')"

# Run dashboard
streamlit run app.py
```

If all commands succeed, dashboard should open in browser at http://localhost:8501

---

## 🎯 Known Limitations

### Expected Behavior:

1. **No recycling data for Algeria:** This is normal - Algeria is not in the OECD dataset
2. **Limited sector data:** Only households and services data available for Algeria
3. **Blue info box on first run:** This is helpful guidance, not an error
4. **Some metrics show N/A:** Normal when cleaned data hasn't been generated yet

### Not Errors:

- "Run data prep notebook for advanced features" → Helpful tip
- Missing comparison countries in some charts → Limited data availability
- Gaps in certain years → Reflects actual data availability

---

## ✅ Success Indicators

You'll know it's working when:

- ✅ Dashboard opens in browser
- ✅ You see 5 navigation options in sidebar
- ✅ Charts are visible and interactive
- ✅ Year slider works
- ✅ Data displays in tables
- ✅ No red error messages (blue info boxes are fine!)

---

## 📞 Quick Reference

**Main command:**
```powershell
streamlit run app.py
```

**Alternative:**
```powershell
python -m streamlit run app.py
```

**Different port:**
```powershell
streamlit run app.py --server.port 8502
```

**Stop dashboard:**
Press `Ctrl+C` in PowerShell terminal

---

**Last Updated:** October 27, 2025

**Status:** Dashboard is ready to run! 🚀
