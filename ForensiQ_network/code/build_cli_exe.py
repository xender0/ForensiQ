import PyInstaller.__main__
import os
import sys

def build_cli_exe():
    args = [
        'main.py',
        '--name=ForensiQ-CLI',
        '--onefile',
        '--icon=NONE',
        '--add-data=forensics;forensics',
        '--add-data=utils;utils',
        '--hidden-import=scapy',
        '--hidden-import=scapy.all',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=matplotlib',
        '--hidden-import=seaborn',
        '--hidden-import=click',
        '--hidden-import=colorama',
        '--hidden-import=jinja2',
        '--hidden-import=plotly',
        '--hidden-import=pyshark',
        '--hidden-import=dpkt',
        '--collect-all=scapy',
        '--collect-all=matplotlib',
        '--noconfirm',
        '--clean',
    ]
    
    print("Building ForensiQ (Network) CLI executable...")
    print("This may take several minutes...")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "="*60)
        print("Build completed successfully!")
        print("="*60)
        print(f"Executable location: dist/ForensiQ-CLI.exe")
        print("\nNote: The first run may be slower as Windows Defender scans the new executable.")
    except Exception as e:
        print(f"\nError during build: {e}")
        print("\nMake sure PyInstaller is installed:")
        print("  pip install pyinstaller")
        sys.exit(1)


if __name__ == '__main__':
    build_cli_exe()

