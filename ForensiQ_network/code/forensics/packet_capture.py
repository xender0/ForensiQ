

import os
import time
from datetime import datetime
from typing import Optional, Callable
from scapy.all import sniff, wrpcap, get_if_list, get_if_addr, IP, TCP, UDP, ICMP, Ether
import threading


class PacketCapture:
    
    
    def __init__(self, interface: Optional[str] = None, 
                 output_file: Optional[str] = None,
                 filter: Optional[str] = None,
                 count: int = 0):
        
        self.interface = interface or self._get_default_interface()
        self.output_file = output_file
        self.filter = filter
        self.count = count
        self.packets = []
        self.is_capturing = False
        self.capture_thread = None
        self.packet_count = 0
        self.start_time = None
        
    def _get_default_interface(self) -> str:
        
        interfaces = get_if_list()
        if not interfaces:
            return 'eth0'
        
        for iface in interfaces:
            if 'loopback' in iface.lower() or 'lo' in iface.lower():
                continue
            try:
                addr = get_if_addr(iface)
                if addr and addr != '0.0.0.0' and not addr.startswith('169.254'):
                    return iface
            except:
                continue
        
        for iface in interfaces:
            if 'loopback' not in iface.lower() and 'lo' not in iface.lower():
                return iface
        
        return interfaces[0]
    
    def _packet_handler(self, packet):
        self.packets.append(packet)
        self.packet_count += 1
        
        if IP in packet:
            src = packet[IP].src
            dst = packet[IP].dst
            proto = packet[IP].proto
            print(f"[{self.packet_count}] {src} -> {dst} (Proto: {proto})")
        
        if self.count > 0 and self.packet_count >= self.count:
            self.stop()
    
    def start(self, duration: Optional[int] = None):
        if self.is_capturing:
            print("Capture already in progress!")
            return
        
        self.is_capturing = True
        self.start_time = datetime.now()
        self.packet_count = 0
        self.packets = []
        
        print(f"Starting packet capture on interface: {self.interface}")
        if self.filter:
            print(f"Filter: {self.filter}")
        
        def capture():
            try:
                sniff(iface=self.interface,
                      filter=self.filter,
                      prn=self._packet_handler,
                      count=self.count if self.count > 0 else 0,
                      stop_filter=lambda x: not self.is_capturing)
            except Exception as e:
                print(f"Error during capture: {e}")
                self.is_capturing = False
        
        self.capture_thread = threading.Thread(target=capture, daemon=True)
        self.capture_thread.start()
        
                               
        if duration:
            def stop_after_duration():
                time.sleep(duration)
                if self.is_capturing:
                    self.stop()
            threading.Thread(target=stop_after_duration, daemon=True).start()
    
    def stop(self):
        
        if not self.is_capturing:
            return
        
        self.is_capturing = False
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        print(f"\nCapture stopped. Total packets: {self.packet_count}")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.output_file and self.packets:
            self.save_to_file(self.output_file)
            print(f"Packets saved to: {self.output_file}")
        
        return self.packets
    
    def save_to_file(self, filename: str):
        
        if not self.packets:
            print("No packets to save!")
            return
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        wrpcap(filename, self.packets)
        print(f"Saved {len(self.packets)} packets to {filename}")
    
    def get_statistics(self) -> dict:
        
        stats = {
            'total_packets': len(self.packets),
            'interface': self.interface,
            'filter': self.filter,
            'start_time': self.start_time.isoformat() if self.start_time else None
        }
        
        if self.packets:
            protocols = {}
            ip_packets = 0
            tcp_packets = 0
            udp_packets = 0
            
            for packet in self.packets:
                if IP in packet:
                    ip_packets += 1
                    proto = packet[IP].proto
                    if TCP in packet:
                        tcp_packets += 1
                        protocols['TCP'] = protocols.get('TCP', 0) + 1
                    elif UDP in packet:
                        udp_packets += 1
                        protocols['UDP'] = protocols.get('UDP', 0) + 1
                    elif ICMP in packet:
                        protocols['ICMP'] = protocols.get('ICMP', 0) + 1
                    else:
                        protocols[f'Proto-{proto}'] = protocols.get(f'Proto-{proto}', 0) + 1
            
            stats['ip_packets'] = ip_packets
            stats['tcp_packets'] = tcp_packets
            stats['udp_packets'] = udp_packets
            stats['protocols'] = protocols
        
        return stats
    
    @staticmethod
    def list_interfaces():
        
        interfaces = get_if_list()
        print("Available network interfaces:")
        print()
        
        active_interface = None
        for iface in interfaces:
            try:
                addr = get_if_addr(iface)
                is_loopback = 'loopback' in iface.lower() or 'lo' in iface.lower()
                is_active = addr and addr != '0.0.0.0' and not addr.startswith('169.254') and not is_loopback
                
                status = ""
                if is_loopback:
                    status = " (Loopback)"
                elif is_active:
                    status = " (ACTIVE - Recommended)"
                    if not active_interface:
                        active_interface = iface
                elif addr == '0.0.0.0':
                    status = " (Inactive)"
                elif addr.startswith('169.254'):
                    status = " (APIPA - No DHCP)"
                
                print(f"  - {iface}: {addr}{status}")
            except Exception as e:
                print(f"  - {iface}: (Error: {e})")
        
        if active_interface:
            print()
            print(f"Recommended interface: {active_interface}")
            print(f"  Use: python main.py capture -i \"{active_interface}\" -o capture.pcap")
        
        return interfaces
    
    @staticmethod
    def get_active_interface() -> Optional[str]:
        
        interfaces = get_if_list()
        for iface in interfaces:
            if 'loopback' in iface.lower() or 'lo' in iface.lower():
                continue
            try:
                addr = get_if_addr(iface)
                if addr and addr != '0.0.0.0' and not addr.startswith('169.254'):
                    return iface
            except:
                continue
        return None

