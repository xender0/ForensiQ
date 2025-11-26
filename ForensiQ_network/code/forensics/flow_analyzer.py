

from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from scapy.all import rdpcap, IP, TCP, UDP
from datetime import datetime
import pandas as pd


class FlowAnalyzer:
    
    
    def __init__(self, pcap_file: Optional[str] = None, packets: Optional[List] = None):
        
        if pcap_file:
            self.packets = rdpcap(pcap_file)
        elif packets:
            self.packets = packets
        else:
            raise ValueError("Either pcap_file or packets must be provided")
        
        self.flows = []
        self.flow_dict = {}
    
    def extract_flows(self, timeout: int = 600) -> List[Dict]:
        
        flows = defaultdict(lambda: {
            'src_ip': '',
            'dst_ip': '',
            'src_port': 0,
            'dst_port': 0,
            'protocol': '',
            'packets': 0,
            'bytes': 0,
            'start_time': None,
            'end_time': None,
            'flags': set(),
            'packet_list': []
        })
        
        for packet in self.packets:
            if IP not in packet:
                continue
            
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            
                                          
            if TCP in packet:
                protocol = 'TCP'
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                flags = packet[TCP].flags
            elif UDP in packet:
                protocol = 'UDP'
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport
                flags = None
            else:
                continue
            
                                                                             
            if protocol == 'TCP':
                flow_key = tuple(sorted([(src_ip, src_port), (dst_ip, dst_port)]))
            else:
                flow_key = ((src_ip, src_port), (dst_ip, dst_port))
            
            flow = flows[flow_key]
            flow['src_ip'] = src_ip
            flow['dst_ip'] = dst_ip
            flow['src_port'] = src_port
            flow['dst_port'] = dst_port
            flow['protocol'] = protocol
            flow['packets'] += 1
            flow['bytes'] += len(packet)
            
            if packet.time:
                timestamp = datetime.fromtimestamp(packet.time)
                if flow['start_time'] is None or timestamp < flow['start_time']:
                    flow['start_time'] = timestamp
                if flow['end_time'] is None or timestamp > flow['end_time']:
                    flow['end_time'] = timestamp
            
            if flags:
                flow['flags'].add(flags)
            
            flow['packet_list'].append(packet)
        
                                
        self.flows = []
        for flow_key, flow_data in flows.items():
            flow_dict = {
                'src_ip': flow_data['src_ip'],
                'dst_ip': flow_data['dst_ip'],
                'src_port': flow_data['src_port'],
                'dst_port': flow_data['dst_port'],
                'protocol': flow_data['protocol'],
                'packets': flow_data['packets'],
                'bytes': flow_data['bytes'],
                'start_time': flow_data['start_time'],
                'end_time': flow_data['end_time'],
                'duration': (flow_data['end_time'] - flow_data['start_time']).total_seconds() 
                           if flow_data['start_time'] and flow_data['end_time'] else 0,
                'flags': list(flow_data['flags']) if flow_data['flags'] else [],
                'packets_per_second': flow_data['packets'] / max(
                    (flow_data['end_time'] - flow_data['start_time']).total_seconds(), 1
                ) if flow_data['start_time'] and flow_data['end_time'] else 0
            }
            self.flows.append(flow_dict)
        
        self.flow_dict = flows
        return self.flows
    
    def get_flow_statistics(self) -> Dict:
        
        if not self.flows:
            self.extract_flows()
        
        total_flows = len(self.flows)
        total_packets = sum(f['packets'] for f in self.flows)
        total_bytes = sum(f['bytes'] for f in self.flows)
        
        protocols = defaultdict(int)
        for flow in self.flows:
            protocols[flow['protocol']] += 1
        
                     
        src_ips = defaultdict(int)
        dst_ips = defaultdict(int)
        for flow in self.flows:
            src_ips[flow['src_ip']] += flow['bytes']
            dst_ips[flow['dst_ip']] += flow['bytes']
        
        top_sources = sorted(src_ips.items(), key=lambda x: x[1], reverse=True)[:10]
        top_destinations = sorted(dst_ips.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_flows': total_flows,
            'total_packets': total_packets,
            'total_bytes': total_bytes,
            'protocols': dict(protocols),
            'top_source_ips': top_sources,
            'top_destination_ips': top_destinations,
            'average_flow_duration': sum(f['duration'] for f in self.flows) / total_flows if total_flows > 0 else 0,
            'average_flow_size': total_bytes / total_flows if total_flows > 0 else 0
        }
    
    def find_suspicious_flows(self, config: Optional[Dict] = None) -> List[Dict]:
        
        if not self.flows:
            self.extract_flows()
        
                            
        default_config = {
            'high_packet_count': 10000,
            'large_transfer_mb': 10,
            'scan_duration': 1,           
            'scan_packets': 100,
        }
        cfg = {**default_config, **(config or {})}
        
        suspicious = []
        
                                                      
        if self.flows:
            avg_packets = sum(f['packets'] for f in self.flows) / len(self.flows)
            avg_bytes = sum(f['bytes'] for f in self.flows) / len(self.flows)
            avg_duration = sum(f['duration'] for f in self.flows) / len(self.flows)
        else:
            avg_packets = avg_bytes = avg_duration = 0
        
        for flow in self.flows:
            flags = []
            
                                                                            
            if flow['packets'] > cfg['high_packet_count']:
                flags.append(f'High packet count ({flow["packets"]} packets, avg: {avg_packets:.0f})')
            elif avg_packets > 0 and flow['packets'] > avg_packets * 5:
                flags.append(f'Unusually high packet count relative to baseline ({flow["packets"]} vs {avg_packets:.0f} avg)')
            
                                                                             
            transfer_mb = flow['bytes'] / (1024 * 1024)
            if transfer_mb > cfg['large_transfer_mb']:
                flags.append(f'Large data transfer ({transfer_mb:.1f} MB)')
            elif avg_bytes > 0 and flow['bytes'] > avg_bytes * 10:
                flags.append(f'Unusually large transfer relative to baseline ({transfer_mb:.1f} MB vs {avg_bytes/(1024*1024):.1f} MB avg)')
            
                                                                                               
            if flow['duration'] < cfg['scan_duration'] and flow['packets'] > cfg['scan_packets']:
                flags.append(f'Potential port scan: {flow["packets"]} packets in {flow["duration"]:.2f}s')
            
                                                                                                 
                                                                    
            if flow['dst_port'] > 49152:                                       
                flags.append(f'Unusual destination port: {flow["dst_port"]} (ephemeral range, possible P2P/C2)')
            
                                                                              
            if flow['src_port'] > 49152 and flow['dst_port'] > 49152:
                flags.append(f'Both ports in ephemeral range ({flow["src_port"]} <-> {flow["dst_port"]}), possible P2P/C2')
            
                                                                        
            if flow['protocol'] == 'TCP' and flow['flags']:
                                                                                           
                                                           
                flag_values = flow['flags']
                
                                                 
                if 1 in flag_values:             
                    flags.append('FIN scan pattern detected')
                if 41 in flag_values:                      
                    flags.append('XMAS scan pattern detected')
                if 0 in flag_values:             
                    flags.append('NULL scan pattern detected')
                if 3 in flag_values:                              
                    flags.append('SYN-FIN pattern (malicious)')
                
                                                                                
                                                                                            
                if 4 in flag_values and 18 not in flag_values:                       
                    flags.append('RST without established connection')
            
            if flags:
                suspicious_flow = flow.copy()
                suspicious_flow['suspicious_reasons'] = flags
                suspicious.append(suspicious_flow)
        
        return suspicious
    
    def export_to_csv(self, filename: str):
        
        if not self.flows:
            self.extract_flows()
        
        df = pd.DataFrame(self.flows)
                                             
        df['start_time'] = df['start_time'].apply(lambda x: x.isoformat() if x else '')
        df['end_time'] = df['end_time'].apply(lambda x: x.isoformat() if x else '')
        df['flags'] = df['flags'].apply(lambda x: ','.join(map(str, x)) if x else '')
        
        df.to_csv(filename, index=False)
        print(f"Exported {len(self.flows)} flows to {filename}")
    
    def get_flows_by_ip(self, ip_address: str) -> List[Dict]:
        
        if not self.flows:
            self.extract_flows()
        
        return [f for f in self.flows 
                if f['src_ip'] == ip_address or f['dst_ip'] == ip_address]
    
    def get_flows_by_port(self, port: int) -> List[Dict]:
        
        if not self.flows:
            self.extract_flows()
        
        return [f for f in self.flows 
                if f['src_port'] == port or f['dst_port'] == port]

