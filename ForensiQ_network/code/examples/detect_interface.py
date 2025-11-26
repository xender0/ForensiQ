

import sys
from pathlib import Path

                                                  
sys.path.insert(0, str(Path(__file__).parent.parent))

from forensics import PacketCapture

def main():
    print("Network Interface Detection Example")
    print("=" * 50)
    
                                               
    print("\n1. All available interfaces:")
    PacketCapture.list_interfaces()
    
                                                  
    print("\n2. Auto-detecting active interface...")
    active_iface = PacketCapture.get_active_interface()
    
    if active_iface:
        print(f"[OK] Active interface found: {active_iface}")
        print(f"\nYou can use this interface for capture:")
        print(f'  python main.py capture -i "{active_iface}" -o capture.pcap')
        print(f"\nOr use auto-detection:")
        print(f'  python main.py capture -i auto -o capture.pcap')
    else:
        print("[X] No active interface found")
        print("  Make sure you're connected to a network")
    
                           
    print("\n3. Using in Python code:")
    print()

if __name__ == '__main__':
    main()

