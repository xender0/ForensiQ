# ForensiQ (Windows) - Complete Feature List

## 🎯 Core Features

### 1. **Export Functionality** ✅
- **HTML Export**: Export individual reports as HTML files
- **CSV Export**: Export table data to CSV format
- **JSON Export**: Export data in JSON format
- **ZIP Export**: Export all reports as a single ZIP archive
- **Export Menu**: Dropdown menu with multiple format options

### 2. **Report Comparison** ✅
- Compare two reports side-by-side
- View differences between scans
- Modal interface for easy selection
- Row count comparison

### 3. **Advanced Search & Filtering** ✅
- **Report Search**: Search through report names in sidebar
- **Table Search**: Search within loaded report tables
- **Global Search**: Search across all reports (placeholder for server-side)
- Real-time filtering
- Case-insensitive search

### 4. **Alerting System** ✅
- Automatic security alerts on suspicious findings
- Alert categories: High, Medium, Low severity
- Alert types:
  - New administrator accounts
  - Firewall configuration changes
  - Suspicious processes
  - Network anomalies
- Alert badge in navbar
- Alert viewer modal
- Acknowledge alerts functionality

### 5. **Data Visualization** ✅
- **Dashboard Statistics Cards**: 
  - Total Reports
  - System Reports
  - Security Reports
  - Network Reports
- **Charts**:
  - Pie chart for report categories
  - Bar chart for report distribution
  - Interactive Chart.js visualizations

### 6. **Report Archiving** ✅
- Automatic archiving with timestamps
- Archive management
- Archive restoration
- Configurable retention period
- Archive metadata tracking

### 7. **Configuration Management** ✅
- Persistent settings storage
- Theme preferences (Dark/Light)
- Alert configuration
- Archive settings
- API key management
- Scan profile saving/loading

### 8. **Theme Toggle** ✅
- Dark theme (default)
- Light theme option
- Theme preference persistence
- Smooth theme switching

### 9. **Column Sorting** ✅
- Click column headers to sort
- Ascending/Descending toggle
- Visual sort indicators (↑ ↓)
- Numeric and text sorting
- Maintains pagination

### 10. **Copy to Clipboard** ✅
- Copy entire table to clipboard
- Tab-separated format
- Quick access button
- Success feedback

### 11. **Enhanced Dashboard** ✅
- Statistics overview
- Recent reports table
- Quick action buttons
- Visual statistics cards
- Category breakdown

### 12. **Improved Report Viewer** ✅
- Report metadata display
- Row count information
- Report type categorization
- Export options per report
- Better error handling

### 13. **Pagination** ✅
- 50 rows per page (configurable)
- Previous/Next navigation
- Page information display
- Works with search filtering

### 14. **Web Server Integration** ✅
- Automatic local web server startup
- CORS support
- Port management
- Fallback to file:// with warnings

## 🔧 Technical Features

### Backend Modules
- **config_manager.py**: Configuration persistence
- **alert_system.py**: Security alert generation
- **report_archiver.py**: Report archiving system
- **export_utils.py**: Export functionality

### Frontend Enhancements
- Modern Bootstrap 5 UI
- Chart.js integration
- Responsive design
- Dark/Light theme support
- Interactive elements

## 📊 Usage

### Exporting Reports
1. Click "Export" button in report view
2. Select format: HTML, CSV, or JSON
3. File downloads automatically

### Comparing Reports
1. Click "Compare" in navbar
2. Select two reports from dropdowns
3. View comparison results

### Viewing Alerts
1. Click "Alerts" button (shows badge if alerts exist)
2. View all unacknowledged alerts
3. Acknowledge alerts as needed

### Sorting Tables
1. Click any column header
2. Click again to reverse sort
3. Visual indicators show sort direction

### Copying Data
1. Load a report
2. Click "Copy" button
3. Paste into Excel/Sheets/etc.

### Archiving
1. Use "Archive" button in main GUI
2. Reports saved with timestamp
3. Access archives from archive folder

## 🚀 Future Enhancements (Planned)

- Report scheduling
- Email notifications
- Advanced report comparison with diff highlighting
- Risk scoring system
- Compliance checking
- Multi-system scanning
- API integration
- Machine learning anomaly detection

## 📝 Notes

- Some features require additional Python packages (see requirements.txt)
- PDF export requires `reportlab` and `beautifulsoup4`
- All data stored locally
- No external dependencies for core functionality

