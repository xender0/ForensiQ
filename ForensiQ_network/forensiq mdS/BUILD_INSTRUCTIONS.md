# Building SpikeGuard Executable (.exe)

This guide explains how to create a standalone executable file for SpikeGuard.

## Prerequisites

1. **Python 3.8+** installed on Windows
2. **All dependencies** installed (run `pip install -r requirements.txt`)
3. **PyInstaller** installed (see installation below)

## Installation

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Install Additional Build Dependencies (if needed)

```bash
pip install pyinstaller-hooks-contrib
```

## Building the Executable

### Option 1: Build GUI Version (Recommended)

The GUI version is the easiest to use:

```bash
python build_exe.py
```

This will create `dist/SpikeGuard.exe`

### Option 2: Build CLI Version

For command-line interface:

```bash
python build_cli_exe.py
```

This will create `dist/SpikeGuard-CLI.exe`

### Option 3: Manual Build with PyInstaller

#### GUI Version:
```bash
pyinstaller --name=SpikeGuard --onefile --windowed --add-data="forensics;forensics" --add-data="utils;utils" --hidden-import=scapy --hidden-import=scapy.all --collect-all=scapy --collect-all=matplotlib gui.py
```

#### CLI Version:
```bash
pyinstaller --name=SpikeGuard-CLI --onefile --add-data="forensics;forensics" --add-data="utils;utils" --hidden-import=scapy --hidden-import=scapy.all --collect-all=scapy --collect-all=matplotlib main.py
```

## Output Location

After building, you'll find the executable in:
- **GUI**: `dist/SpikeGuard.exe`
- **CLI**: `dist/SpikeGuard-CLI.exe`

## Important Notes

### File Size
The executable will be large (50-100MB+) because it includes:
- Python interpreter
- All required libraries (Scapy, Pandas, Matplotlib, etc.)
- All dependencies

### First Run
- Windows Defender may flag the new executable (false positive)
- You may need to allow it through Windows Defender
- The first run may be slower as Windows scans the file

### Requirements for End Users
- **No Python installation required** - the .exe is standalone
- **Npcap required** - Users still need Npcap installed for live packet capture on Windows
  - Download from: https://nmap.org/npcap/
  - Install with "WinPcap API-compatible Mode" enabled

### Troubleshooting

#### "Module not found" errors
- Add missing modules to `--hidden-import` flags
- Use `--collect-all=<module>` for complex packages

#### Large file size
- This is normal for Python executables with many dependencies
- Consider using `--onedir` instead of `--onefile` for faster startup (but multiple files)

#### Antivirus warnings
- PyInstaller executables are often flagged by antivirus software
- This is a false positive - you can submit to antivirus vendors for whitelisting
- Users may need to add exception in their antivirus

#### Missing DLL errors
- Ensure Visual C++ Redistributables are installed
- May need to include additional DLLs with `--add-binary`

## Distribution

### What to Include
1. **SpikeGuard.exe** (or SpikeGuard-CLI.exe)
2. **README.md** - User documentation
3. **Npcap installer** - For Windows users who need live capture
4. **License file** - If required

### What NOT to Include
- Python installation files
- Source code (unless open source distribution)
- Development dependencies

## Advanced Options

### Adding an Icon
1. Create or obtain an `.ico` file
2. Add to build command: `--icon=spikeguard.ico`

### Reducing File Size
- Use `--exclude-module` to exclude unused modules
- Use `--onedir` instead of `--onefile` (creates folder with multiple files)

### Code Signing (for distribution)
For professional distribution, consider code signing:
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com SpikeGuard.exe
```

## Testing the Executable

Before distributing:
1. Test on a clean Windows machine (without Python installed)
2. Test all major features:
   - GUI launch
   - Packet capture
   - PCAP analysis
   - Intrusion detection
   - Report generation
3. Test with different Windows versions if possible

## Support

For build issues, check:
- PyInstaller documentation: https://pyinstaller.org/
- SpikeGuard GitHub issues
- Python packaging forums

