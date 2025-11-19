# Quick Guide: Building SpikeGuard .exe

## Quick Start (3 Steps)

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Build the Executable
**Option A - Using the build script (Easiest):**
```bash
python build_exe.py
```

**Option B - Using batch file (Windows):**
Double-click `build.bat`

**Option C - Manual command:**
```bash
pyinstaller --name=SpikeGuard --onefile --windowed --add-data="forensics;forensics" --add-data="utils;utils" --hidden-import=scapy --hidden-import=scapy.all --collect-all=scapy --collect-all=matplotlib gui.py
```

### Step 3: Find Your Executable
After building, your executable will be in:
```
dist/SpikeGuard.exe
```

## That's It!

The executable is standalone - no Python installation needed for end users.

## Important Notes

1. **File Size**: The .exe will be 50-100MB+ (includes Python and all libraries)
2. **Npcap Required**: Users still need Npcap for live packet capture on Windows
3. **Antivirus**: Windows Defender may flag it initially (false positive)
4. **First Run**: May be slow as Windows scans the new file

## Troubleshooting

**"Module not found" error?**
- Run: `pip install -r requirements.txt`
- Then rebuild

**Build fails?**
- Make sure all dependencies are installed
- Check that you're in the project directory
- Try: `pip install --upgrade pyinstaller`

**Need help?**
- See `BUILD_INSTRUCTIONS.md` for detailed guide

