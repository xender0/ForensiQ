

import os
from collections import defaultdict
from typing import List, Dict, Optional
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, DNS, load_layer
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.dns import DNSQR, DNSRR

                              
try:
    load_layer("http")
except:
    pass
import pandas as pd


class ProtocolAnalyzer:
    
    
    def __init__(self, pcap_file: Optional[str] = None, packets: Optional[List] = None):
        
        if pcap_file and os.path.exists(pcap_file):
            self.packets = rdpcap(pcap_file)
            self.source = pcap_file
        elif packets:
            self.packets = packets
            self.source = "packet_list"
        else:
            raise ValueError("Either pcap_file or packets must be provided")
        
        self.analysis_results = {}
        self.http_data = []
        self.dns_data = []
        self.tcp_connections = []
        self.udp_sessions = []
    
    def analyze(self):
        
        print("Starting protocol analysis...")
        
        self._analyze_ip_traffic()
        self._analyze_tcp()
        self._analyze_udp()
        self._analyze_http()
        self._analyze_dns()
        self._analyze_icmp()
        
        print("Protocol analysis complete!")
        return self.analysis_results
    
    def _analyze_ip_traffic(self):
        
        ip_stats = {
            'total_packets': len(self.packets),
            'ip_packets': 0,
            'source_ips': defaultdict(int),
            'destination_ips': defaultdict(int),
            'protocols': defaultdict(int),
            'total_bytes': 0
        }
        
        for packet in self.packets:
            if IP in packet:
                ip_stats['ip_packets'] += 1
                ip_stats['source_ips'][packet[IP].src] += 1
                ip_stats['destination_ips'][packet[IP].dst] += 1
                ip_stats['protocols'][packet[IP].proto] += 1
                ip_stats['total_bytes'] += len(packet)
        
        self.analysis_results['ip_traffic'] = ip_stats
    
    def _analyze_tcp(self):
        
        tcp_connections = defaultdict(lambda: {
            'packets': 0,
            'bytes': 0,
            'flags': set(),
            'ports': set()
        })
        
        for packet in self.packets:
                                   
            if TCP in packet and IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
                
                                                       
                conn_key = tuple(sorted([(src_ip, src_port), (dst_ip, dst_port)]))
                
                tcp_connections[conn_key]['packets'] += 1
                tcp_connections[conn_key]['bytes'] += len(packet)
                tcp_connections[conn_key]['flags'].add(packet[TCP].flags)
                tcp_connections[conn_key]['ports'].add(src_port)
                tcp_connections[conn_key]['ports'].add(dst_port)
        
        self.analysis_results['tcp_connections'] = {
            'total_connections': len(tcp_connections),
            'connections': dict(tcp_connections)
        }
    
    def _analyze_udp(self):
        
        udp_stats = {
            'total_udp_packets': 0,
            'source_ports': defaultdict(int),
            'destination_ports': defaultdict(int),
            'total_bytes': 0
        }
        
        for packet in self.packets:
            if UDP in packet:
                udp_stats['total_udp_packets'] += 1
                udp_stats['source_ports'][packet[UDP].sport] += 1
                udp_stats['destination_ports'][packet[UDP].dport] += 1
                udp_stats['total_bytes'] += len(packet)
        
        self.analysis_results['udp_traffic'] = udp_stats
    
    def _analyze_http(self):
        
        http_requests = []
        http_responses = []
        
        for packet in self.packets:
                                    
            if IP not in packet:
                continue
                
            if HTTPRequest in packet:
                req = packet[HTTPRequest]
                http_requests.append({
                    'method': req.Method.decode() if req.Method else 'N/A',
                    'host': req.Host.decode() if req.Host else 'N/A',
                    'path': req.Path.decode() if req.Path else 'N/A',
                    'src_ip': packet[IP].src,
                    'dst_ip': packet[IP].dst,
                    'user_agent': req.User_Agent.decode() if req.User_Agent else 'N/A'
                })
            
            if HTTPResponse in packet:
                resp = packet[HTTPResponse]
                http_responses.append({
                    'status_code': resp.Status_Code.decode() if resp.Status_Code else 'N/A',
                    'reason': resp.Reason_Phrase.decode() if resp.Reason_Phrase else 'N/A',
                    'src_ip': packet[IP].src,
                    'dst_ip': packet[IP].dst
                })
        
        self.http_data = {
            'requests': http_requests,
            'responses': http_responses,
            'total_requests': len(http_requests),
            'total_responses': len(http_responses)
        }
        self.analysis_results['http_traffic'] = self.http_data
    
    def _analyze_dns(self):
        
        dns_queries = []
        dns_responses = []
        
        for packet in self.packets:
                                                               
            if DNS in packet:
                                                 
                src_ip = 'N/A'
                dst_ip = 'N/A'
                if IP in packet:
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                
                dns = packet[DNS]
                
                if DNSQR in dns:
                    for qr in dns[DNSQR]:
                        dns_queries.append({
                            'query': qr.qname.decode().rstrip('.') if qr.qname else 'N/A',
                            'type': qr.qtype,
                            'src_ip': src_ip,
                            'dst_ip': dst_ip
                        })
                
                if DNSRR in dns:
                    for rr in dns[DNSRR]:
                        dns_responses.append({
                            'name': rr.rrname.decode().rstrip('.') if rr.rrname else 'N/A',
                            'type': rr.type,
                            'data': rr.rdata if hasattr(rr, 'rdata') else 'N/A',
                            'src_ip': src_ip,
                            'dst_ip': dst_ip
                        })
        
        self.dns_data = {
            'queries': dns_queries,
            'responses': dns_responses,
            'total_queries': len(dns_queries),
            'total_responses': len(dns_responses)
        }
        self.analysis_results['dns_traffic'] = self.dns_data
    
    def _analyze_icmp(self):
        
        icmp_stats = {
            'total_icmp_packets': 0,
            'types': defaultdict(int),
            'codes': defaultdict(int)
        }
        
        for packet in self.packets:
            if ICMP in packet:
                icmp_stats['total_icmp_packets'] += 1
                icmp_stats['types'][packet[ICMP].type] += 1
                icmp_stats['codes'][packet[ICMP].code] += 1
        
        self.analysis_results['icmp_traffic'] = icmp_stats
    
    def get_top_ips(self, top_n: int = 10) -> Dict:
        
        if 'ip_traffic' not in self.analysis_results:
            self._analyze_ip_traffic()
        
        ip_stats = self.analysis_results['ip_traffic']
        top_sources = sorted(ip_stats['source_ips'].items(), 
                            key=lambda x: x[1], reverse=True)[:top_n]
        top_destinations = sorted(ip_stats['destination_ips'].items(), 
                                 key=lambda x: x[1], reverse=True)[:top_n]
        
        return {
            'top_sources': top_sources,
            'top_destinations': top_destinations
        }
    
    def export_http_to_csv(self, filename: str):
        
        if not self.http_data:
            self._analyze_http()
        
        if self.http_data['requests']:
            df = pd.DataFrame(self.http_data['requests'])
            df.to_csv(filename, index=False)
            print(f"HTTP requests exported to {filename}")
    
    def export_dns_to_csv(self, filename: str):
        
        if not self.dns_data:
            self._analyze_dns()
        
        if self.dns_data['queries']:
            df = pd.DataFrame(self.dns_data['queries'])
            df.to_csv(filename, index=False)
            print(f"DNS queries exported to {filename}")
    
    def generate_report(self) -> str:
        
        report = []
        report.append("=" * 60)
        report.append("PROTOCOL ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Source: {self.source}")
        report.append(f"Total Packets: {len(self.packets)}")
        report.append("")
        
        if 'ip_traffic' in self.analysis_results:
            ip = self.analysis_results['ip_traffic']
            report.append("IP Traffic Statistics:")
            report.append(f"  IP Packets: {ip['ip_packets']}")
            report.append(f"  Total Bytes: {ip['total_bytes']:,}")
            report.append("")
            
            top_ips = self.get_top_ips(5)
            report.append("Top 5 Source IPs:")
            for ip_addr, count in top_ips['top_sources']:
                report.append(f"  {ip_addr}: {count} packets")
            report.append("")
        
        if 'tcp_connections' in self.analysis_results:
            tcp = self.analysis_results['tcp_connections']
            report.append(f"TCP Connections: {tcp['total_connections']}")
            report.append("")
        
        if 'http_traffic' in self.analysis_results:
            http = self.analysis_results['http_traffic']
            report.append(f"HTTP Requests: {http['total_requests']}")
            report.append(f"HTTP Responses: {http['total_responses']}")
            report.append("")
        
        if 'dns_traffic' in self.analysis_results:
            dns = self.analysis_results['dns_traffic']
            report.append(f"DNS Queries: {dns['total_queries']}")
            report.append(f"DNS Responses: {dns['total_responses']}")
            report.append("")
        
        return "\n".join(report)

