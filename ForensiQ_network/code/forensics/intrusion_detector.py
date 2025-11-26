

from collections import defaultdict, Counter
from typing import List, Dict, Optional, Set, Tuple
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, DNS
from datetime import datetime, timedelta
import re


class IntrusionDetector:
    
    
    def __init__(self, pcap_file: Optional[str] = None, packets: Optional[List] = None,
                 config: Optional[Dict] = None):
        
        if pcap_file:
            self.packets = rdpcap(pcap_file)
        elif packets:
            self.packets = packets
        else:
            raise ValueError("Either pcap_file or packets must be provided")
        
        self.threats = []
        self.anomalies = []
        
                                                                          
        default_config = {
                                  
            'port_scan_ports_threshold': 50,
            'port_scan_time_window': 60,           
            
                                     
            'flood_time_window': 60,           
            'flood_multiplier': 10,                   
            
                                  
            'syn_flood_count': 100,
            'syn_flood_time_window': 5,           
            'syn_ack_ratio_threshold': 0.1,                                        
            
                             
            'icmp_time_window': 60,           
            'icmp_multiplier': 5,
            
                            
            'dns_time_window': 60,           
            'dns_multiplier': 10,
            'dns_nxdomain_ratio_threshold': 0.5,                              
            'dns_long_domain_threshold': 100,              
            
                                
            'unusual_port_count': 20,
            
                                      
            'flow_high_packet_count': 10000,
            'flow_large_transfer_mb': 10,
            'flow_scan_duration': 1,           
            'flow_scan_packets': 100,
        }
        
        self.config = {**default_config, **(config or {})}
        
                                                              
        self.suspicious_ports = {4444, 31337, 12345, 6667, 6666, 6665}                         
        self.known_malicious_ips = set()                                             
        
                                       
        self.tcp_connections = {}                                                 
        
                                       
        self.packet_timestamps = []
        
    def detect_anomalies(self) -> List[Dict]:
        
        print("Starting enhanced intrusion detection analysis...")
        
        self.threats = []
        self.anomalies = []
        
                                                              
        self._extract_timestamps()
        
                                   
        self._detect_port_scans()
        self._detect_stealth_scans()
        self._detect_suspicious_ports()
        self._detect_flood_attacks()
        self._detect_icmp_anomalies()
        self._detect_tcp_anomalies()
        self._detect_unusual_traffic_patterns()
        self._detect_dns_anomalies()
        self.check_malicious_ips()
        
                                                     
        self._correlate_alerts()
        
        all_findings = self.threats + self.anomalies
        print(f"Detection complete. Found {len(all_findings)} potential threats/anomalies.")
        
        return all_findings
    
    def _extract_timestamps(self):
        
        self.packet_timestamps = []
        for packet in self.packets:
            if hasattr(packet, 'time') and packet.time:
                self.packet_timestamps.append(packet.time)
        
        if self.packet_timestamps:
            self.start_time = min(self.packet_timestamps)
            self.end_time = max(self.packet_timestamps)
            self.duration = self.end_time - self.start_time
        else:
            self.start_time = 0
            self.end_time = 0
            self.duration = 0
    
    def _get_packets_in_window(self, start_time: float, window_seconds: float) -> List:
        
        end_time = start_time + window_seconds
        return [pkt for pkt in self.packets 
                if hasattr(pkt, 'time') and start_time <= pkt.time <= end_time]
    
    def _detect_port_scans(self):
        
                                     
        window_seconds = self.config['port_scan_time_window']
        scan_threshold = self.config['port_scan_ports_threshold']
        
                                     
        window_scans = defaultdict(lambda: {'ports': set(), 'targets': set(), 'packets': []})
        
        for packet in self.packets:
            if IP in packet and TCP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                dst_port = packet[TCP].dport
                pkt_time = packet.time if hasattr(packet, 'time') else 0
                
                                     
                window_key = int(pkt_time / window_seconds)
                key = (src_ip, window_key)
                
                window_scans[key]['ports'].add(dst_port)
                window_scans[key]['targets'].add(dst_ip)
                window_scans[key]['packets'].append(packet)
        
                                                            
        for (src_ip, window), data in window_scans.items():
            ports_count = len(data['ports'])
            if ports_count > scan_threshold:
                self.threats.append({
                    'type': 'Port Scan',
                    'severity': 'High',
                    'source_ip': src_ip,
                    'description': f'Potential port scan: {src_ip} scanned {ports_count} different ports within {window_seconds}s window',
                    'ports_scanned': ports_count,
                    'targets': len(data['targets']),
                    'time_window_seconds': window_seconds,
                    'timestamp': window * window_seconds
                })
    
    def _detect_stealth_scans(self):
        
                                            
                                            
                                 
        
        stealth_packets = defaultdict(list)
        
        for packet in self.packets:
            if IP in packet and TCP in packet:
                flags = packet[TCP].flags
                src_ip = packet[IP].src
                dst_port = packet[TCP].dport
                
                                                 
                is_stealth = False
                scan_type = None
                
                                     
                if flags == 1:
                    is_stealth = True
                    scan_type = 'FIN Scan'
                                                             
                elif flags == 41:
                    is_stealth = True
                    scan_type = 'XMAS Scan'
                                                 
                elif flags == 0:
                    is_stealth = True
                    scan_type = 'NULL Scan'
                                                   
                elif (flags & 1) and (flags & 16) and not (flags & 2):                       
                    is_stealth = True
                    scan_type = 'ACK-FIN Scan'
                
                if is_stealth:
                    key = (src_ip, dst_port)
                    stealth_packets[key].append((packet, scan_type))
        
                                                
        src_stealth = defaultdict(lambda: {'ports': set(), 'types': set(), 'count': 0})
        for (src_ip, dst_port), packets in stealth_packets.items():
            src_stealth[src_ip]['ports'].add(dst_port)
            for pkt, scan_type in packets:
                src_stealth[src_ip]['types'].add(scan_type)
                src_stealth[src_ip]['count'] += 1
        
                                                         
        for src_ip, data in src_stealth.items():
            if data['count'] > 10 or len(data['ports']) > 5:
                self.threats.append({
                    'type': 'Stealth Port Scan',
                    'severity': 'High',
                    'source_ip': src_ip,
                    'description': f'Stealth port scan detected: {src_ip} used {", ".join(data["types"])} on {len(data["ports"])} ports',
                    'scan_types': list(data['types']),
                    'ports_scanned': len(data['ports']),
                    'packet_count': data['count']
                })
    
    def _detect_suspicious_ports(self):
        
        suspicious_connections = defaultdict(lambda: {'inbound': 0, 'outbound': 0, 'packets': []})
        
                                                                         
                                           
        private_ranges = [
            ('10.0.0.0', '10.255.255.255'),
            ('172.16.0.0', '172.31.255.255'),
            ('192.168.0.0', '192.168.255.255'),
        ]
        
        def is_private_ip(ip):
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            try:
                ip_int = int(parts[0]) * 256**3 + int(parts[1]) * 256**2 + int(parts[2]) * 256 + int(parts[3])
                for start, end in private_ranges:
                    start_parts = start.split('.')
                    end_parts = end.split('.')
                    start_int = int(start_parts[0]) * 256**3 + int(start_parts[1]) * 256**2 + int(start_parts[2]) * 256 + int(start_parts[3])
                    end_int = int(end_parts[0]) * 256**3 + int(end_parts[1]) * 256**2 + int(end_parts[2]) * 256 + int(end_parts[3])
                    if start_int <= ip_int <= end_int:
                        return True
            except:
                pass
            return False
        
        for packet in self.packets:
            if IP in packet and TCP in packet:
                dst_port = packet[TCP].dport
                if dst_port in self.suspicious_ports:
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                    key = (src_ip, dst_ip, dst_port)
                    
                                                                                                    
                    is_inbound = not is_private_ip(src_ip) and is_private_ip(dst_ip)
                    is_outbound = is_private_ip(src_ip) and not is_private_ip(dst_ip)
                    
                    if is_inbound:
                        suspicious_connections[key]['inbound'] += 1
                    elif is_outbound:
                        suspicious_connections[key]['outbound'] += 1
                    else:
                        suspicious_connections[key]['inbound'] += 1           
                    
                    suspicious_connections[key]['packets'].append(packet)
        
        for (src_ip, dst_ip, port), data in suspicious_connections.items():
            direction = 'inbound' if data['inbound'] > data['outbound'] else 'outbound'
            count = data['inbound'] + data['outbound']
            
            severity = 'High' if direction == 'outbound' else 'Medium'                               
            
            self.threats.append({
                'type': 'Suspicious Port',
                'severity': severity,
                'source_ip': src_ip,
                'destination_ip': dst_ip,
                'port': port,
                'direction': direction,
                'description': f'{direction.capitalize()} connection to suspicious port {port} from {src_ip} to {dst_ip}',
                'packet_count': count
            })
    
    def _detect_flood_attacks(self):
        
        window_seconds = self.config['flood_time_window']
        multiplier = self.config['flood_multiplier']
        
                                                          
        window_data = defaultdict(lambda: {'packets': 0, 'bytes': 0, 'ips': set()})
        
        for packet in self.packets:
            if IP in packet:
                src_ip = packet[IP].src
                pkt_time = packet.time if hasattr(packet, 'time') else 0
                window_key = int(pkt_time / window_seconds)
                
                window_data[window_key]['packets'] += 1
                window_data[window_key]['bytes'] += len(packet)
                window_data[window_key]['ips'].add(src_ip)
        
                                            
        ip_window_counts = defaultdict(lambda: defaultdict(int))
        ip_window_bytes = defaultdict(lambda: defaultdict(int))
        
        for packet in self.packets:
            if IP in packet:
                src_ip = packet[IP].src
                pkt_time = packet.time if hasattr(packet, 'time') else 0
                window_key = int(pkt_time / window_seconds)
                
                ip_window_counts[src_ip][window_key] += 1
                ip_window_bytes[src_ip][window_key] += len(packet)
        
                                                                
        for window_key, window_info in window_data.items():
            if window_info['packets'] == 0:
                continue
            
            avg_packets_per_ip = window_info['packets'] / max(len(window_info['ips']), 1)
            threshold = avg_packets_per_ip * multiplier
            
                                          
            for src_ip in window_info['ips']:
                ip_count = ip_window_counts[src_ip][window_key]
                if ip_count > threshold:
                    self.threats.append({
                        'type': 'Potential Flood Attack',
                        'severity': 'High',
                        'source_ip': src_ip,
                        'description': f'Potential flood attack: {src_ip} sent {ip_count} packets in {window_seconds}s window (threshold: {threshold:.0f})',
                        'packet_count': ip_count,
                        'bytes_sent': ip_window_bytes[src_ip][window_key],
                        'time_window_seconds': window_seconds,
                        'timestamp': window_key * window_seconds
                    })
    
    def _detect_icmp_anomalies(self):
        
        window_seconds = self.config['icmp_time_window']
        multiplier = self.config['icmp_multiplier']
        
                                       
        icmp_window_data = defaultdict(lambda: defaultdict(lambda: {'count': 0, 'types': Counter(), 'sizes': []}))
        
        for packet in self.packets:
            if ICMP in packet:
                src_ip = packet[IP].src
                icmp_type = packet[ICMP].type
                pkt_time = packet.time if hasattr(packet, 'time') else 0
                window_key = int(pkt_time / window_seconds)
                
                icmp_window_data[window_key][src_ip]['count'] += 1
                icmp_window_data[window_key][src_ip]['types'][icmp_type] += 1
                icmp_window_data[window_key][src_ip]['sizes'].append(len(packet))
        
                             
        for window_key, ip_data in icmp_window_data.items():
            if not ip_data:
                continue
            
                                                          
            total_icmp = sum(data['count'] for data in ip_data.values())
            avg_icmp = total_icmp / max(len(ip_data), 1)
            threshold = avg_icmp * multiplier
            
            for src_ip, data in ip_data.items():
                if data['count'] > threshold:
                    icmp_types = dict(data['types'])
                    avg_size = sum(data['sizes']) / len(data['sizes']) if data['sizes'] else 0
                    
                                                 
                    anomaly_details = []
                    if icmp_types.get(8, 0) > threshold * 0.8:                             
                        anomaly_details.append('Ping Flood (Echo Requests)')
                    if icmp_types.get(3, 0) > threshold * 0.5:                           
                        anomaly_details.append('High Destination Unreachable (possible network mapping)')
                    if icmp_types.get(11, 0) > threshold * 0.5:                 
                        anomaly_details.append('High Time Exceeded (possible port scanning)')
                    if avg_size > 1000:                      
                        anomaly_details.append(f'Large ICMP packets (avg: {avg_size:.0f} bytes, possible data exfiltration)')
                    
                    description = f'High ICMP traffic from {src_ip}: {data["count"]} packets in {window_seconds}s'
                    if anomaly_details:
                        description += f' - {", ".join(anomaly_details)}'
                    
                    self.anomalies.append({
                        'type': 'ICMP Anomaly',
                        'severity': 'Medium',
                        'source_ip': src_ip,
                        'description': description,
                        'packet_count': data['count'],
                        'icmp_types': icmp_types,
                        'average_packet_size': avg_size,
                        'time_window_seconds': window_seconds
                    })
    
    def _detect_tcp_anomalies(self):
        
        window_seconds = self.config['syn_flood_time_window']
        syn_threshold = self.config['syn_flood_count']
        syn_ack_ratio_threshold = self.config['syn_ack_ratio_threshold']
        
                                                                     
        syn_data = defaultdict(lambda: defaultdict(int))
        syn_ack_data = defaultdict(lambda: defaultdict(int))
        tcp_flags = defaultdict(lambda: defaultdict(Counter))
        
                                     
        connections = {}                                                 
        
        for packet in self.packets:
            if TCP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                flags = packet[TCP].flags
                pkt_time = packet.time if hasattr(packet, 'time') else 0
                window_key = int(pkt_time / window_seconds)
                
                conn_key = (src_ip, src_port, dst_ip, dst_port)
                
                                   
                if flags == 2:            
                    syn_data[src_ip][window_key] += 1
                    connections[conn_key] = 'SYN_SENT'
                
                                                         
                elif flags == 18:           
                    syn_ack_data[src_ip][window_key] += 1
                    if conn_key in connections:
                        connections[conn_key] = 'ESTABLISHED'
                
                                             
                tcp_flags[src_ip][window_key][flags] += 1
                
                                                  
                self._analyze_tcp_flags(src_ip, flags, conn_key, connections)
        
                                                               
        for src_ip, window_counts in syn_data.items():
            for window_key, syn_count in window_counts.items():
                if syn_count > syn_threshold:
                    syn_ack_count = syn_ack_data[src_ip].get(window_key, 0)
                    syn_ack_ratio = syn_ack_count / syn_count if syn_count > 0 else 0
                    
                                                                                           
                    if syn_ack_ratio < syn_ack_ratio_threshold:
                        self.threats.append({
                            'type': 'Potential SYN Flood',
                            'severity': 'High',
                            'source_ip': src_ip,
                            'description': f'Potential SYN flood: {src_ip} sent {syn_count} SYN packets in {window_seconds}s with only {syn_ack_count} SYN-ACK responses (ratio: {syn_ack_ratio:.2%})',
                            'syn_count': syn_count,
                            'syn_ack_count': syn_ack_count,
                            'syn_ack_ratio': syn_ack_ratio,
                            'time_window_seconds': window_seconds
                        })
    
    def _analyze_tcp_flags(self, src_ip: str, flags: int, conn_key: Tuple, connections: Dict):
        
                                            
        malicious_patterns = {
            3: ('SYN-FIN', 'High'),                              
            41: ('XMAS Scan', 'High'),                           
            0: ('NULL Scan', 'High'),            
            1: ('FIN Scan', 'Medium'),                                
            4: ('RST without connection', 'Medium'),             
        }
        
                                               
        if flags in malicious_patterns:
            pattern_name, severity = malicious_patterns[flags]
            
                                                                     
            if flags in [1, 4] and conn_key not in connections:
                                                           
                self.anomalies.append({
                    'type': 'Unusual TCP Flags',
                    'severity': severity,
                    'source_ip': src_ip,
                    'description': f'{pattern_name} detected from {src_ip} - {self._flag_to_string(flags)}',
                    'flag_value': flags,
                    'flag_name': pattern_name
                })
        elif flags == 40:                           
            self.anomalies.append({
                'type': 'Unusual TCP Flags',
                'severity': 'High',
                'source_ip': src_ip,
                'description': f'XMAS-like scan pattern (PSH-URG-RST) from {src_ip}',
                'flag_value': flags,
                'flag_name': 'XMAS-like Scan'
            })
    
    def _flag_to_string(self, flags: int) -> str:
        
        flag_names = []
        if flags & 1: flag_names.append('FIN')
        if flags & 2: flag_names.append('SYN')
        if flags & 4: flag_names.append('RST')
        if flags & 8: flag_names.append('PSH')
        if flags & 16: flag_names.append('ACK')
        if flags & 32: flag_names.append('URG')
        return '-'.join(flag_names) if flag_names else 'None'
    
    def _detect_unusual_traffic_patterns(self):
        
        port_usage = defaultdict(lambda: {'ports': set(), 'duration': 0, 'start_time': None})
        
        for packet in self.packets:
            if IP in packet and TCP in packet:
                src_ip = packet[IP].src
                dst_port = packet[TCP].dport
                pkt_time = packet.time if hasattr(packet, 'time') else 0
                
                port_usage[src_ip]['ports'].add(dst_port)
                if port_usage[src_ip]['start_time'] is None:
                    port_usage[src_ip]['start_time'] = pkt_time
                port_usage[src_ip]['duration'] = max(port_usage[src_ip]['duration'], 
                                                      pkt_time - port_usage[src_ip]['start_time'])
        
                                                                          
                                                            
        for src_ip, data in port_usage.items():
            ports_count = len(data['ports'])
            duration_hours = data['duration'] / 3600 if data['duration'] > 0 else 0
            
                                                                                
                                                                
            if ports_count > self.config['unusual_port_count'] and duration_hours > 1:
                self.anomalies.append({
                    'type': 'Unusual Port Usage',
                    'severity': 'Low',
                    'source_ip': src_ip,
                    'description': f'Unusual port usage: {src_ip} accessed {ports_count} different ports over {duration_hours:.1f} hours',
                    'unique_ports': ports_count,
                    'duration_hours': duration_hours
                })
    
    def _detect_dns_anomalies(self):
        
        window_seconds = self.config['dns_time_window']
        multiplier = self.config['dns_multiplier']
        nxdomain_threshold = self.config['dns_nxdomain_ratio_threshold']
        long_domain_threshold = self.config['dns_long_domain_threshold']
        
        dns_window_data = defaultdict(lambda: defaultdict(lambda: {
            'queries': 0, 'nxdomain': 0, 'query_types': Counter(), 
            'domain_lengths': [], 'external_queries': 0
        }))
        
        for packet in self.packets:
            if IP in packet and UDP in packet and packet[UDP].dport == 53:
                src_ip = packet[IP].src
                pkt_time = packet.time if hasattr(packet, 'time') else 0
                window_key = int(pkt_time / window_seconds)
                
                data = dns_window_data[window_key][src_ip]
                data['queries'] += 1
                
                                        
                try:
                    if DNS in packet:
                        dns = packet[DNS]
                        
                                          
                        if hasattr(dns, 'qd') and dns.qd:
                            query_name = str(dns.qd.qname, 'utf-8', errors='ignore')
                            data['domain_lengths'].append(len(query_name))
                            
                                                                                   
                            if len(query_name) > long_domain_threshold:
                                data['long_domains'] = data.get('long_domains', 0) + 1
                            
                                              
                            if hasattr(dns.qd, 'qtype'):
                                data['query_types'][dns.qd.qtype] += 1
                        
                                                            
                        if hasattr(dns, 'rcode') and dns.rcode == 3:
                            data['nxdomain'] += 1
                        
                                                                                               
                        if hasattr(dns, 'qd') and dns.qd and hasattr(dns.qd, 'qtype'):
                            qtype = dns.qd.qtype
                            if qtype in [16, 10]:                         
                                data['unusual_query_types'] = data.get('unusual_query_types', 0) + 1
                except:
                    pass                                  
        
                             
        for window_key, ip_data in dns_window_data.items():
            if not ip_data:
                continue
            
            total_queries = sum(data['queries'] for data in ip_data.values())
            avg_queries = total_queries / max(len(ip_data), 1)
            threshold = avg_queries * multiplier
            
            for src_ip, data in ip_data.items():
                if data['queries'] > threshold:
                    nxdomain_ratio = data['nxdomain'] / data['queries'] if data['queries'] > 0 else 0
                    avg_domain_length = sum(data['domain_lengths']) / len(data['domain_lengths']) if data['domain_lengths'] else 0
                    
                    anomaly_details = []
                    
                                        
                    if nxdomain_ratio > nxdomain_threshold:
                        anomaly_details.append(f'High NXDOMAIN rate ({nxdomain_ratio:.1%}) - possible C2 domain probing or data exfiltration')
                    
                                         
                    if data.get('unusual_query_types', 0) > data['queries'] * 0.3:
                        anomaly_details.append('High volume of TXT/NULL queries - possible DNS exfiltration')
                    
                                       
                    if data.get('long_domains', 0) > data['queries'] * 0.2:
                        anomaly_details.append('Many long domain names - possible DNS tunneling')
                    
                                                
                    if avg_domain_length > 50:
                        anomaly_details.append(f'Unusually long domain names (avg: {avg_domain_length:.0f} chars)')
                    
                    description = f'High DNS query rate from {src_ip}: {data["queries"]} queries in {window_seconds}s'
                    if anomaly_details:
                        description += f' - {"; ".join(anomaly_details)}'
                    
                    self.anomalies.append({
                        'type': 'DNS Anomaly',
                        'severity': 'Medium',
                        'source_ip': src_ip,
                        'description': description,
                        'query_count': data['queries'],
                        'nxdomain_ratio': nxdomain_ratio,
                        'query_types': dict(data['query_types']),
                        'average_domain_length': avg_domain_length,
                        'time_window_seconds': window_seconds
                    })
    
    def _correlate_alerts(self):
        
                                   
        ip_alerts = defaultdict(list)
        
        for threat in self.threats:
            if 'source_ip' in threat:
                ip_alerts[threat['source_ip']].append(threat)
        
        for anomaly in self.anomalies:
            if 'source_ip' in anomaly:
                ip_alerts[anomaly['source_ip']].append(anomaly)
        
                                      
        for src_ip, alerts in ip_alerts.items():
            if len(alerts) < 2:
                continue
            
            alert_types = [a.get('type', '') for a in alerts]
            
                                                                        
            if 'Suspicious Port' in alert_types and 'Known Malicious IP' in alert_types:
                                          
                suspicious_port_alert = next((a for a in alerts if a.get('type') == 'Suspicious Port'), None)
                malicious_ip_alert = next((a for a in alerts if a.get('type') == 'Known Malicious IP'), None)
                
                if suspicious_port_alert and malicious_ip_alert:
                    self.threats.append({
                        'type': 'Established C2 Channel',
                        'severity': 'Critical',
                        'source_ip': src_ip,
                        'description': f'Correlated alert: {src_ip} connecting to suspicious port on known malicious IP - likely established C2 channel',
                        'correlated_alerts': ['Suspicious Port', 'Known Malicious IP'],
                        'port': suspicious_port_alert.get('port'),
                        'malicious_ip': malicious_ip_alert.get('destination_ip')
                    })
            
                                                                 
            high_severity_count = sum(1 for a in alerts if a.get('severity') in ['High', 'Critical'])
            if high_severity_count >= 3:
                self.threats.append({
                    'type': 'Multiple High-Severity Alerts',
                    'severity': 'Critical',
                    'source_ip': src_ip,
                    'description': f'Multiple high-severity alerts ({high_severity_count}) from {src_ip} - possible coordinated attack',
                    'alert_count': high_severity_count,
                    'alert_types': alert_types
                })
    
    def get_threat_summary(self) -> Dict:
        
        if not self.threats and not self.anomalies:
            self.detect_anomalies()
        
        threat_types = Counter(t['type'] for t in self.threats)
        anomaly_types = Counter(a['type'] for a in self.anomalies)
        
        severity_counts = Counter(t['severity'] for t in self.threats)
        
        return {
            'total_threats': len(self.threats),
            'total_anomalies': len(self.anomalies),
            'threat_types': dict(threat_types),
            'anomaly_types': dict(anomaly_types),
            'severity_breakdown': dict(severity_counts),
            'unique_source_ips': len(set(t.get('source_ip', '') for t in self.threats + self.anomalies))
        }
    
    def generate_alert_report(self) -> str:
        
        if not self.threats and not self.anomalies:
            self.detect_anomalies()
        
        report = []
        report.append("=" * 60)
        report.append("ENHANCED INTRUSION DETECTION ALERT REPORT")
        report.append("=" * 60)
        report.append("")
        
        summary = self.get_threat_summary()
        report.append("SUMMARY:")
        report.append(f"  Total Threats: {summary['total_threats']}")
        report.append(f"  Total Anomalies: {summary['total_anomalies']}")
        report.append(f"  Unique Source IPs: {summary['unique_source_ips']}")
        report.append("")
        
                           
        severity_order = ['Critical', 'High', 'Medium', 'Low']
        threats_by_severity = defaultdict(list)
        for threat in self.threats:
            threats_by_severity[threat.get('severity', 'Low')].append(threat)
        
        for severity in severity_order:
            if threats_by_severity[severity]:
                report.append(f"{severity.upper()} SEVERITY THREATS:")
                for i, threat in enumerate(threats_by_severity[severity], 1):
                    report.append(f"  {i}. [{threat['severity']}] {threat['type']}")
                    report.append(f"     Source: {threat.get('source_ip', 'N/A')}")
                    report.append(f"     {threat['description']}")
                    if 'correlated_alerts' in threat:
                        report.append(f"     Correlated from: {', '.join(threat['correlated_alerts'])}")
                    report.append("")
        
        if self.anomalies:
            report.append("ANOMALIES:")
            for i, anomaly in enumerate(self.anomalies, 1):
                report.append(f"  {i}. [{anomaly['severity']}] {anomaly['type']}")
                report.append(f"     Source: {anomaly.get('source_ip', 'N/A')}")
                report.append(f"     {anomaly['description']}")
                report.append("")
        
        return "\n".join(report)
    
    def add_malicious_ip(self, ip_address: str):
        
        self.known_malicious_ips.add(ip_address)
    
    def load_malicious_ips_from_file(self, filepath: str):
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    ip = line.strip()
                    if ip and not ip.startswith('
                        self.known_malicious_ips.add(ip)
        except Exception as e:
            print(f"Warning: Could not load malicious IPs from {filepath}: {e}")
    
    def check_malicious_ips(self):
        
        malicious_found = []
        
        for packet in self.packets:
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                
                if src_ip in self.known_malicious_ips:
                    malicious_found.append({
                        'type': 'Known Malicious IP',
                        'severity': 'High',
                        'source_ip': src_ip,
                        'destination_ip': dst_ip,
                        'description': f'Traffic from known malicious IP: {src_ip} to {dst_ip}'
                    })
                elif dst_ip in self.known_malicious_ips:
                    malicious_found.append({
                        'type': 'Known Malicious IP',
                        'severity': 'High',
                        'source_ip': src_ip,
                        'destination_ip': dst_ip,
                        'description': f'Traffic to known malicious IP: {dst_ip} from {src_ip}'
                    })
        
                     
        seen = set()
        unique_malicious = []
        for alert in malicious_found:
            key = (alert['source_ip'], alert['destination_ip'])
            if key not in seen:
                seen.add(key)
                unique_malicious.append(alert)
        
        self.threats.extend(unique_malicious)
        return unique_malicious
