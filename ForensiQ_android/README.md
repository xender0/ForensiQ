# ForensiQ (Android)

A comprehensive Android device forensics tool that extracts detailed information from Android devices using ADB (Android Debug Bridge).

## Features

This tool extracts the following information from connected Android devices:

- **Installed Applications**: Complete list with package names, APK paths, versions, install/update dates, UIDs, and data directories
- **Application Permissions**: All permissions granted to installed applications
- **Device Information**: Model, manufacturer, Android version, hardware specs, battery, storage, and more
- **Filesystem**: Mount points, disk usage, directory structures, partitions, and block devices
- **Location Data**: GPS status, location services, location history, Wi-Fi access points, and apps with location permissions
- **Network Data**: Network interfaces, Wi-Fi networks, Bluetooth devices, VPN info, cellular data, and network statistics

## Prerequisites

1. **ADB (Android Debug Bridge)** must be installed and accessible in your PATH
   - Download from [Android Developer Platform Tools](https://developer.android.com/studio/releases/platform-tools)
   - Or install via package manager:
     - Windows: `choco install adb`
     - macOS: `brew install android-platform-tools`
     - Linux: `sudo apt-get install android-tools-adb`

2. **Python 3.7+** installed

3. **Android Device** with:
   - USB Debugging enabled
   - Developer Options enabled
   - Device connected via USB and authorized for ADB access

## Installation

1. Clone or download this repository
2. Ensure ADB is installed and in your system PATH
3. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Usage

### GUI Version (Recommended)

1. Connect your Android device via USB
2. Enable USB debugging on the device
3. Authorize the computer when prompted on the device
4. Run the GUI application:

```bash
python gui.py
```

The GUI allows you to:
- **Select which data to extract** - Check/uncheck specific extraction types
- **Monitor progress** - Real-time progress bar and log output
- **Choose output location** - Select where to save the results
- **View extraction log** - See detailed extraction progress and status
- **Stop extraction** - Cancel the process at any time

### Command-Line Version

1. Connect your Android device via USB
2. Enable USB debugging on the device
3. Authorize the computer when prompted on the device
4. Run the main script:

```bash
python main.py
```

The tool will:
- Check for ADB connection
- Extract all available information from the device
- Save results to a JSON file: `forensics_output_YYYYMMDD_HHMMSS.json`

## Output Format

The output JSON file contains:

```json
{
  "collection_timestamp": "2025-01-26T08:19:52.298216",
  "installed_apps": [
    {
      "package_name": "com.example.app",
      "apk_path": "/data/app/com.example.app.apk",
      "label": "Example App",
      "version": "1.0.0",
      "install_date": "2024-01-15 10:30:00",
      "update_date": "2024-12-20 14:22:00",
      "uid": "10001",
      "data_dir": "/data/data/com.example.app"
    }
  ],
  "app_permissions": {
    "com.example.app": [
      "android.permission.INTERNET",
      "android.permission.ACCESS_FINE_LOCATION"
    ]
  },
  "device_info": {
    "model": "Pixel 7",
    "manufacturer": "Google",
    "android_version": "14",
    ...
  },
  "filesystem": { ... },
  "location": { ... },
  "network": { ... }
}
```

## Module Structure

```
ForensiQ/
├── main.py                 # Command-line entry point
├── gui.py                  # GUI entry point (recommended)
├── example_usage.py        # Example usage script
├── requirements.txt        # Dependencies
├── README.md              # This file
└── src/
    ├── __init__.py
    ├── utils.py           # ADB utility functions
    └── extractors/
        ├── __init__.py
        ├── apps.py        # Application extraction
        ├── permissions.py # Permission extraction
        ├── device_info.py # Device information
        ├── filesystem.py  # Filesystem extraction
        ├── location.py    # Location data
        └── network.py     # Network data
```

## Permissions Note

Some data extraction may require:
- **Root access** for certain filesystem and database locations
- **Special permissions** for sensitive data like IMEI, phone numbers
- **ADB shell permissions** - most extraction works with standard ADB access

The tool will attempt to extract all available information and mark inaccessible data as "N/A".

## Troubleshooting

### "No Android device connected via ADB"
- Ensure USB debugging is enabled: Settings > Developer Options > USB Debugging
- Check ADB connection: `adb devices`
- Try disconnecting and reconnecting the device
- Authorize the computer on the device when prompted

### "Permission denied" errors
- Some extractions require root access
- The tool will continue with available data and mark inaccessible items as "N/A"

### ADB not found
- Ensure ADB is installed and in your system PATH
- Test with: `adb version`

## License

This tool is for educational and authorized forensic analysis purposes only. Ensure you have proper authorization before extracting data from any device.

## Disclaimer

Use this tool responsibly and only on devices you own or have explicit permission to analyze. Unauthorized access to devices is illegal.

