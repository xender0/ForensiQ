# ForensiQ (Windows) - Changelog

## Version 2.0 - Complete Feature Enhancement

### 🎉 Major Features Added

#### Export Functionality
- ✅ HTML export for individual reports
- ✅ CSV export with proper formatting
- ✅ JSON export with structured data
- ✅ ZIP export for all reports (via GUI)
- ✅ Export dropdown menu with multiple formats

#### Report Comparison
- ✅ Side-by-side report comparison
- ✅ Report selection modal
- ✅ Difference detection
- ✅ Row count comparison

#### Advanced Search
- ✅ Report name search in sidebar
- ✅ Table content search
- ✅ Real-time filtering
- ✅ Global search placeholder

#### Alerting System
- ✅ Automatic security alert generation
- ✅ Alert severity levels (High/Medium/Low)
- ✅ Alert categories:
  - New administrator accounts
  - Firewall changes
  - Suspicious processes
  - Network anomalies
- ✅ Alert badge in navbar
- ✅ Alert viewer modal
- ✅ Alert acknowledgment

#### Data Visualization
- ✅ Interactive dashboard with statistics
- ✅ Pie chart for report categories
- ✅ Bar chart for report distribution
- ✅ Chart.js integration
- ✅ Real-time chart updates

#### Report Archiving
- ✅ Automatic report archiving
- ✅ Timestamp-based organization
- ✅ Archive metadata
- ✅ Archive restoration
- ✅ Configurable retention

#### Configuration Management
- ✅ Persistent settings storage
- ✅ Theme preferences
- ✅ Alert configuration
- ✅ Archive settings
- ✅ Settings UI in main GUI

#### UI Enhancements
- ✅ Dark/Light theme toggle
- ✅ Theme preference persistence
- ✅ Column sorting (click headers)
- ✅ Copy to clipboard
- ✅ Enhanced navbar with new buttons
- ✅ Better error messages
- ✅ Loading indicators

#### Report Annotations
- ✅ Add notes to reports
- ✅ Save annotations locally
- ✅ View saved annotations
- ✅ Per-report note storage

### 🔧 Technical Improvements

#### New Modules Created
- `config_manager.py` - Configuration persistence
- `alert_system.py` - Security alert system
- `report_archiver.py` - Report archiving
- `export_utils.py` - Export functionality

#### Enhanced Files
- `run.py` - Integrated all new features
- `index.html` - Complete UI overhaul with all features
- `requirements.txt` - Updated dependencies

### 🐛 Bug Fixes
- Fixed CORS issue with automatic web server
- Improved admin privilege detection
- Better error handling throughout
- Fixed manifest loading issues

### 📝 Documentation
- Created `FEATURES.md` - Complete feature list
- Created `CHANGELOG.md` - This file
- Updated `README.md` - Enhanced instructions

### 🚀 Performance
- Optimized report loading
- Better pagination (50 rows per page)
- Improved search performance
- Faster dashboard updates

## Version 1.0 - Initial Release
- Basic report collection
- HTML report viewer
- PowerShell script execution
- Basic GUI interface

