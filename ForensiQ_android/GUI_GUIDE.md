# ForensiQ (Android) - GUI Guide

## Overview

The GUI version provides an easy-to-use graphical interface for selecting which data to extract from your Android device.

## Getting Started

1. **Launch the GUI:**
   ```bash
   python gui.py
   ```

2. **Check Connection Status:**
   - The GUI will automatically check for ADB connection on startup
   - Status indicator will show:
     - ✓ Green: Device Connected
     - ✗ Red: No Device Connected
   - Click "Refresh Connection" if you connect a device after launching

## Using the GUI

### 1. Connection Status Panel
- Shows current ADB connection status
- "Refresh Connection" button to recheck device connection

### 2. Extraction Options Panel
Select which data types to extract using checkboxes:
- ✅ **Installed Applications** - Extract all installed apps with details
- ✅ **Application Permissions** - Extract permissions for each app
- ✅ **Device Information** - Extract device specs, model, Android version
- ✅ **Filesystem Information** - Extract filesystem structure and mount points
- ✅ **Location Data** - Extract GPS and location-related information
- ✅ **Network Data** - Extract network interfaces, Wi-Fi, Bluetooth

**Quick Actions:**
- **Select All** - Check all extraction options
- **Deselect All** - Uncheck all extraction options

### 3. Output Settings Panel
- **Save to:** Shows where results will be saved
- **Browse...** - Choose a custom output directory (optional)
- Default: Saves to current directory with auto-generated filename

### 4. Progress Panel
- Shows current extraction step and progress
- Progress bar animates during extraction

### 5. Extraction Log Panel
- Real-time log of extraction progress
- Shows timestamps and status for each step
- Scrollable text area

### 6. Action Buttons
- **Start Extraction** - Begin the selected extraction processes
- **Stop** - Cancel the current extraction (only enabled during extraction)
- **Clear Log** - Clear the extraction log display
- **Open Output Folder** - Open the folder containing saved results
- **Exit** - Close the application

## Step-by-Step Usage

1. **Connect your Android device** via USB
2. **Enable USB Debugging** on your device
3. **Authorize** the computer when prompted on the device
4. **Launch the GUI** (`python gui.py`)
5. **Verify connection** - Status should show "✓ Device Connected"
6. **Select extraction options** - Check/uncheck what you want to extract
7. **(Optional)** Choose output location using "Browse..."
8. **Click "Start Extraction"**
9. **Monitor progress** in the log panel
10. **Wait for completion** - A message will appear when done
11. **Find your results** - Click "Open Output Folder" or check the output location

## Features

### Selective Extraction
- Extract only the data you need
- Faster execution when extracting fewer data types
- Saves disk space with smaller output files

### Real-time Monitoring
- See extraction progress as it happens
- Detailed log entries with timestamps
- Progress bar shows activity

### User-Friendly
- Clear visual feedback
- Error messages for common issues
- Automatic connection checking

### Flexible Output
- Choose where to save results
- Auto-generated filenames with timestamps
- Easy access to output files

## Tips

- **Selective Extraction**: For faster results, only select what you need
- **Monitor Logs**: Keep an eye on the log panel for any errors or warnings
- **Stop Anytime**: You can stop extraction if needed using the Stop button
- **Multiple Runs**: Run multiple extractions with different selections
- **Save Location**: Remember your chosen output location for easy access

## Troubleshooting

### "No Device Connected"
- Check USB connection
- Ensure USB Debugging is enabled
- Try clicking "Refresh Connection"
- Verify ADB is installed: `adb devices` in terminal

### Extraction Stuck
- Check the log panel for error messages
- Try stopping and restarting
- Disconnect and reconnect the device

### GUI Not Responding
- During extraction, the GUI may appear slow but should remain responsive
- Check the log panel to see if extraction is still running
- If truly frozen, close and restart the application

