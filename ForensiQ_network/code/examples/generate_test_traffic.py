

import argparse
import sys
from scapy.all import *
from random import randint, choice
import time
from datetime import datetime

                         
import warnings
warnings.filterwarnings("ignore")


class TestTrafficGenerator:
    
    
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.packets = []
        self.start_time = time.time()
        self.packet_count = 0
        
                  
        self.attacker_ip = "192.168.1.100"
        self.victim_ip = "192.168.1.1"
        self.internal_ip = "10.0.0.50"
        self.external_ip = "203.0.113.1"
        
    def generate_port_scan(self, duration: int = 30):
        
        print(f"Generating port scan traffic...")
        end_time = self.start_time + duration
        
        ports_scanned = set()
        current_time = self.start_time
        
        while current_time < end_time and len(ports_scanned) < 60:
                               
            dst_port = randint(1, 65535)
            ports_scanned.add(dst_port)
            
                               
            pkt = IP(src=self.attacker_ip, dst=self.victim_ip) /\
                  TCP(sport=randint(49152, 65535), dport=dst_port, flags="S")
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            
                                         
            current_time += 0.1
        
        print(f"  Generated {len(ports_scanned)} port scan packets")
    
    def generate_syn_flood(self, duration: int = 10):
        
        print(f"Generating SYN flood...")
        end_time = self.start_time + duration
        current_time = self.start_time
        syn_count = 0
        
        while current_time < end_time and syn_count < 150:
                               
            pkt = IP(src=self.attacker_ip, dst=self.victim_ip) /\
                  TCP(sport=randint(49152, 65535), dport=80, flags="S")
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            syn_count += 1
            
                                        
            current_time += 0.03
        
        print(f"  Generated {syn_count} SYN packets")
    
    def generate_stealth_scans(self, duration: int = 20):
        
        print(f"Generating stealth scans...")
        end_time = self.start_time + duration
        current_time = self.start_time
        
        scan_types = [
            ("FIN", 1),                
            ("XMAS", 41),                        
            ("NULL", 0),                
        ]
        
        scan_count = 0
        while current_time < end_time and scan_count < 50:
            scan_type, flags = choice(scan_types)
            dst_port = randint(1, 1000)
            
            pkt = IP(src=self.attacker_ip, dst=self.victim_ip) /\
                  TCP(sport=randint(49152, 65535), dport=dst_port, flags=flags)
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            scan_count += 1
            
            current_time += 0.2
        
        print(f"  Generated {scan_count} stealth scan packets")
    
    def generate_icmp_flood(self, duration: int = 10):
        
        print(f"Generating ICMP flood...")
        end_time = self.start_time + duration
        current_time = self.start_time
        icmp_count = 0
        
        while current_time < end_time and icmp_count < 200:
                                   
            pkt = IP(src=self.attacker_ip, dst=self.victim_ip) /\
                  ICMP(type=8, code=0)
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            icmp_count += 1
            
            current_time += 0.05
        
                                                   
        for i in range(20):
            pkt = IP(src=self.attacker_ip, dst=self.victim_ip) /\
                  ICMP(type=3, code=0)
            pkt.time = current_time + i * 0.1
            self.packets.append(pkt)
            self.packet_count += 1
        
        print(f"  Generated {icmp_count + 20} ICMP packets")
    
    def generate_dns_anomalies(self, duration: int = 30):
        
        print(f"Generating DNS anomalies...")
        end_time = self.start_time + duration
        current_time = self.start_time
        dns_count = 0
        
                                                     
        long_domains = [
            "a" * 150 + ".example.com",
            "b" * 120 + ".test.com",
            "c" * 200 + ".malicious.com",
        ]
        
                                                 
        normal_domains = ["test{}.com".format(i) for i in range(100)]
        
        while current_time < end_time and dns_count < 150:
                                                    
            if dns_count % 3 == 0:
                domain = choice(long_domains)
            else:
                domain = choice(normal_domains)
            
                              
            dns_query = DNS(rd=1, qd=DNSQR(qname=domain))
            pkt = IP(src=self.internal_ip, dst="8.8.8.8") /\
                  UDP(sport=randint(49152, 65535), dport=53) /\
                  dns_query
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            dns_count += 1
            
            current_time += 0.2
        
        print(f"  Generated {dns_count} DNS queries")
    
    def generate_suspicious_ports(self, duration: int = 20):
        
        print(f"Generating suspicious port connections...")
        end_time = self.start_time + duration
        current_time = self.start_time
        
        suspicious_ports = [4444, 31337, 12345, 6667, 6666, 6665]
        
        for port in suspicious_ports:
                                                       
            pkt = IP(src=self.external_ip, dst=self.internal_ip) /\
                  TCP(sport=randint(49152, 65535), dport=port, flags="S")
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            
                                                                         
            pkt2 = IP(src=self.internal_ip, dst=self.external_ip) /\
                   TCP(sport=randint(49152, 65535), dport=port, flags="S")
            pkt2.time = current_time + 0.1
            self.packets.append(pkt2)
            self.packet_count += 1
            
            current_time += 1
        
        print(f"  Generated connections to {len(suspicious_ports)} suspicious ports")
    
    def generate_normal_traffic(self, duration: int = 30):
        
        print(f"Generating normal traffic...")
        end_time = self.start_time + duration
        current_time = self.start_time
        
                             
        for i in range(20):
                 
            pkt = IP(src=self.internal_ip, dst="93.184.216.34") /\
                  TCP(sport=randint(49152, 65535), dport=80, flags="S")
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            
                     
            pkt2 = IP(src="93.184.216.34", dst=self.internal_ip) /\
                   TCP(sport=80, dport=pkt[TCP].sport, flags="SA")
            pkt2.time = current_time + 0.01
            self.packets.append(pkt2)
            self.packet_count += 1
            
                 
            pkt3 = IP(src=self.internal_ip, dst="93.184.216.34") /\
                   TCP(sport=pkt[TCP].sport, dport=80, flags="A")
            pkt3.time = current_time + 0.02
            self.packets.append(pkt3)
            self.packet_count += 1
            
            current_time += 1.5
        
                            
        normal_domains = ["google.com", "github.com", "stackoverflow.com"]
        for i in range(10):
            domain = choice(normal_domains)
            dns_query = DNS(rd=1, qd=DNSQR(qname=domain))
            pkt = IP(src=self.internal_ip, dst="8.8.8.8") /\
                  UDP(sport=randint(49152, 65535), dport=53) /\
                  dns_query
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            current_time += 2
        
        print(f"  Generated normal traffic packets")
    
    def generate_flood_attack(self, duration: int = 10):
        
        print(f"Generating flood attack...")
        end_time = self.start_time + duration
        current_time = self.start_time
        flood_count = 0
        
        while current_time < end_time and flood_count < 500:
                                
            pkt = IP(src=self.attacker_ip, dst=self.victim_ip) /\
                  TCP(sport=randint(49152, 65535), dport=randint(1, 65535), flags="S")
            pkt.time = current_time
            self.packets.append(pkt)
            self.packet_count += 1
            flood_count += 1
            
            current_time += 0.02
        
        print(f"  Generated {flood_count} flood packets")
    
    def save(self):
        
        print(f"\nSaving {len(self.packets)} packets to {self.output_file}...")
        
                                   
        self.packets.sort(key=lambda p: p.time if hasattr(p, 'time') else 0)
        
                       
        wrpcap(self.output_file, self.packets)
        print(f"✓ Saved {len(self.packets)} packets to {self.output_file}")
        print(f"  File size: {os.path.getsize(self.output_file) / 1024:.2f} KB")


def main():
    parser = argparse.ArgumentParser(description='Generate test traffic with attack patterns')
    parser.add_argument('--output', '-o', default='test_traffic.pcap',
                       help='Output PCAP file (default: test_traffic.pcap)')
    parser.add_argument('--duration', '-d', type=int, default=60,
                       help='Duration in seconds for each attack type (default: 60)')
    parser.add_argument('--attacks', '-a', nargs='+',
                       choices=['all', 'port_scan', 'syn_flood', 'stealth_scan', 
                               'icmp_flood', 'dns_anomaly', 'suspicious_port', 
                               'normal', 'flood'],
                       default=['all'],
                       help='Attack types to generate (default: all)')
    
    args = parser.parse_args()
    
    generator = TestTrafficGenerator(args.output)
    
    if 'all' in args.attacks:
        attacks = ['port_scan', 'syn_flood', 'stealth_scan', 'icmp_flood', 
                  'dns_anomaly', 'suspicious_port', 'normal', 'flood']
    else:
        attacks = args.attacks
    
    print(f"Generating test traffic with {len(attacks)} attack types...")
    print(f"Duration per attack: {args.duration} seconds\n")
    
    for attack in attacks:
        if attack == 'port_scan':
            generator.generate_port_scan(args.duration)
        elif attack == 'syn_flood':
            generator.generate_syn_flood(min(args.duration, 10))
        elif attack == 'stealth_scan':
            generator.generate_stealth_scans(args.duration)
        elif attack == 'icmp_flood':
            generator.generate_icmp_flood(min(args.duration, 10))
        elif attack == 'dns_anomaly':
            generator.generate_dns_anomalies(args.duration)
        elif attack == 'suspicious_port':
            generator.generate_suspicious_ports(args.duration)
        elif attack == 'normal':
            generator.generate_normal_traffic(args.duration)
        elif attack == 'flood':
            generator.generate_flood_attack(min(args.duration, 10))
    
    generator.save()
    
    print(f"\n✓ Test traffic generation complete!")
    print(f"\nTo test the intrusion detection:")
    print(f"  python main.py detect {args.output}")


if __name__ == '__main__':
    import os
    main()

