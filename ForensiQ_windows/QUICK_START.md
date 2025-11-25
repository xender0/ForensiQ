# ForensiQ (Windows) - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python run.py
```
Or double-click `start.bat`

### Step 3: Collect Data
1. Select PowerShell collectors from the list
2. Click "Run Selected Collectors" or "Run All Collectors"
3. Wait for completion
4. Click "📊 View Reports" to see results

## 🎯 Key Features Quick Reference

### Exporting Reports
- **From Report Viewer**: Click "Export" → Choose format (HTML/CSV/JSON)
- **From Main GUI**: Click "📦 Export All" → Creates ZIP file

### Viewing Alerts
- Click "⚠️ Alerts" button in navbar
- Red badge shows unacknowledged alert count
- Acknowledge alerts as you review them

### Comparing Reports
- Click "Compare" in navbar
- Select two reports from dropdowns
- View differences and statistics

### Sorting Tables
- Click any column header to sort
- Click again to reverse sort
- Visual arrows show sort direction

### Adding Notes
- Load a report
- Click "Add Note" in metadata section
- Type your note and save
- Notes persist across sessions

### Archiving
- Click "📚 Archive" in main GUI
- Reports saved with timestamp
- Access from `output/archive/` folder

### Changing Theme
- Click "Theme" button in navbar
- Toggle between Dark and Light
- Preference saved automatically

## 📋 Common Tasks

### Run a Full System Scan
1. Click "▶▶ Run All Collectors"
2. Wait for all scripts to complete
3. View reports in dashboard

### Export All Data
1. Run collectors to generate reports
2. Click "📦 Export All" in main GUI
3. ZIP file created in project folder

### Check for Security Issues
1. Run collectors
2. Check "⚠️ Alerts" button
3. Review any security alerts
4. Investigate flagged items

### Compare Two Scans
1. Run collectors (first scan)
2. Archive reports (optional)
3. Run collectors again (second scan)
4. Click "Compare" → Select both reports

## 💡 Tips

- **Run as Administrator** for full functionality
- **Check Alerts** regularly for security issues
- **Archive Reports** before major system changes
- **Use Search** to quickly find specific data
- **Export to CSV** for Excel analysis
- **Add Notes** to document findings

## 🆘 Troubleshooting

**Reports not showing?**
- Ensure collectors completed successfully
- Check `output/` folder for HTML files
- Click "Refresh" in report viewer

**Export not working?**
- Install optional packages: `pip install reportlab beautifulsoup4`
- Check browser download settings
- Try different export format

**Alerts not appearing?**
- Run collectors first to generate reports
- Check `alerts.json` file exists
- Verify alert system is enabled in settings

**Theme not saving?**
- Check browser localStorage is enabled
- Clear cache and try again
- Use Settings in main GUI

## 📚 More Information

- See `FEATURES.md` for complete feature list
- See `README.md` for detailed documentation
- See `CHANGELOG.md` for version history

