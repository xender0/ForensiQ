# ForensiQ (Windows) - Windows Forensics Toolkit

A comprehensive Windows forensics toolkit for collecting system information, analyzing security data, and generating detailed reports.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+** - [Download Python](https://www.python.org/downloads/)
2. **Windows 10/11** - This toolkit is designed for Windows
3. **PowerShell 5.1+** - Usually pre-installed on Windows
4. **Administrator Privileges** - Required for many collection scripts

### Installation

1. **Clone or download this repository**
   ```bash
   cd Forensiq
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install ttkbootstrap pywin32 pycryptodome requests reportlab beautifulsoup4
   ```

   **Note**: `reportlab` and `beautifulsoup4` are optional but enable PDF export functionality.

3. **Optional: Install PowerShell modules** (for advanced features)
   ```powershell
   Install-Module PSSQLite -Scope CurrentUser -Force
   ```

## 📖 How to Run

### Method 1: Using the Batch File (Easiest)

1. **Double-click `start.bat`**
   - This will automatically launch the GUI application

### Method 2: Using Python Command

1. **Open Command Prompt or PowerShell**
2. **Navigate to the project directory**
   ```bash
   cd path\to\ForensiQ\ForensiQ_windows
   ```
3. **Run the main application**
   ```bash
   python run.py
   ```

### Method 3: Run as Administrator (Recommended)

For full functionality, run as administrator:

1. **Right-click on `start.bat`** or **Command Prompt**
2. **Select "Run as administrator"**
3. **Execute the command**
   ```bash
   python run.py
   ```

## 🎯 Using the Application

### Main GUI (`run.py`)

The main interface provides:

1. **PowerShell Data Collectors**
   - Select individual scripts or run all
   - View progress in real-time
   - Reports are saved to the `output/` folder

2. **Additional Tools**
   - 🔑 **Recover Browser Passwords** - Extract saved passwords from browsers
   - 🛡️ **VirusTotal File Scanner** - Scan files for malware
   - 📧 **Breached Email Checker** - Check if emails were in data breaches
   - 🌐 **Scan Browser History (VT)** - Check URLs in browser history
   - 📶 **Check Insecure Wi-Fi** - Analyze Wi-Fi security

3. **Quick Actions**
   - 📊 **View Reports** - Open the HTML report viewer
   - 📁 **Open Output Folder** - Access generated reports

### Viewing Reports

1. **From the GUI**: Click "📊 View Reports" button
2. **Directly**: Open `index.html` in your web browser
   ```bash
   # Double-click index.html or:
   start index.html
   ```

The report viewer includes:
- 📊 **Dashboard** with statistics and charts
- 🔍 **Advanced Search** for reports and table data
- 📄 **Pagination** for large tables (50 rows per page)
- 📥 **Export options** (HTML, CSV, JSON, ZIP)
- 🔄 **Report Comparison** - Compare two reports side-by-side
- ⚠️ **Alert System** - Security alerts for suspicious findings
- 📈 **Data Visualization** - Interactive charts and graphs
- 🌓 **Theme Toggle** - Dark/Light theme support
- 📋 **Copy to Clipboard** - Quick data copying
- 🔢 **Column Sorting** - Click headers to sort
- 📝 **Report Annotations** - Add notes to reports
- 📚 **Report Archiving** - Automatic timestamped archives
- ⚙️ **Settings Management** - Persistent configuration

## 📁 Project Structure

```
Forensiq/
├── run.py                          # Main GUI application
├── index.html                      # Report viewer (HTML/JS)
├── start.bat                       # Quick launcher
├── output/                         # Generated reports folder
│   ├── manifest.json              # Report index
│   └── *.html                     # Individual reports
├── breached_email_checker/         # Email breach checker
├── *.ps1                           # PowerShell collection scripts
└── README.md                       # This file
```

## 🔧 Available Collection Scripts

The toolkit includes 27+ PowerShell scripts for collecting:

- **System Information**: OS details, system info, computer details
- **Network Data**: IP configs, network adapters, TCP connections, DNS cache
- **Security**: Administrators, firewall rules, Windows Defender status
- **Hardware**: USB devices, cameras, connected devices, disk information
- **Software**: Installed programs, services, scheduled tasks, startup programs
- **User Data**: User details, processes, browser passwords, Wi-Fi passwords

## ⚙️ Configuration

### VirusTotal API Key

Some tools require a VirusTotal API key:
1. Get a free API key from [VirusTotal](https://www.virustotal.com/gui/join-us)
2. Enter it when prompted in the respective tools

### PowerShell Execution Policy

If you encounter execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🐛 Troubleshooting

### "Python not found"
- Ensure Python is installed and added to PATH
- Try using `python3` instead of `python`

### "Module not found" errors
- Install missing dependencies: `pip install <module-name>`
- Ensure you're using the correct Python environment

### "Access Denied" errors
- Run the application as Administrator
- Some scripts require elevated privileges

### Reports not showing
- Ensure scripts have completed successfully
- Check the `output/` folder for generated HTML files
- Refresh the report viewer

### PowerShell script errors
- Check PowerShell execution policy
- Ensure you're running as Administrator
- Verify all PowerShell scripts are present in the project root

## 📝 Notes

- **First Run**: The application will create the `output/` folder automatically
- **Admin Rights**: Many collection scripts require administrator privileges for full functionality
- **Report Generation**: Reports are generated as HTML files in the `output/` folder
- **Manifest**: The `manifest.json` file is automatically updated when reports are generated

## ✨ New Features (Version 2.0)

### Export & Sharing
- **Multiple Export Formats**: HTML, CSV, JSON, ZIP
- **Copy to Clipboard**: Quick data copying for spreadsheets
- **Export Menu**: Easy access to all export options

### Analysis & Comparison
- **Report Comparison**: Compare two scans side-by-side
- **Column Sorting**: Click any column header to sort
- **Advanced Search**: Search reports and table contents
- **Data Visualization**: Interactive charts and statistics

### Security & Monitoring
- **Alert System**: Automatic alerts for suspicious findings
- **Alert Categories**: Administrators, Firewall, Processes, Network
- **Alert Severity**: High, Medium, Low classifications
- **Alert Badge**: Visual indicator in navbar

### Organization & Management
- **Report Archiving**: Automatic timestamped archives
- **Report Annotations**: Add notes to reports
- **Settings Management**: Persistent configuration
- **Theme Support**: Dark/Light theme toggle

### Enhanced UI
- **Modern Dashboard**: Statistics cards and charts
- **Better Navigation**: Improved sidebar and controls
- **Responsive Design**: Works on different screen sizes
- **Visual Feedback**: Loading indicators and status messages

## 🔒 Security & Privacy

- This toolkit accesses sensitive system information
- All data is stored locally in the `output/` folder
- No data is transmitted externally (except VirusTotal API calls if used)
- Configuration and annotations stored locally
- Use responsibly and in accordance with your organization's policies

## 📄 License

This project is provided as-is for educational and forensic purposes.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in the console
3. Ensure all prerequisites are installed

---

**ForensiQ (Windows)** - Professional Windows Forensics Toolkit

