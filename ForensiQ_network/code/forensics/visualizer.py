

import os
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter, defaultdict
import pandas as pd
import seaborn as sns
from datetime import datetime


class NetworkVisualizer:
    
    
    def __init__(self, output_dir: str = "visualizations"):
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
                   
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            try:
                plt.style.use('seaborn-darkgrid')
            except:
                plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_traffic_over_time(self, packets: List, filename: Optional[str] = None):
        
        if not packets:
            print("No packets to visualize")
            return
        
        timestamps = []
        sizes = []
        
        for packet in packets:
            if hasattr(packet, 'time') and packet.time:
                timestamps.append(datetime.fromtimestamp(packet.time))
                sizes.append(len(packet))
        
        if not timestamps:
            print("No valid timestamps found")
            return
        
        df = pd.DataFrame({'time': timestamps, 'size': sizes})
        df = df.set_index('time').resample('1S').sum()
        
        plt.figure(figsize=(14, 6))
        plt.plot(df.index, df['size'], linewidth=1.5)
        plt.title('Network Traffic Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Bytes per Second', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
            print(f"Saved visualization to {filename}")
        else:
            plt.savefig(os.path.join(self.output_dir, 'traffic_over_time.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_protocol_distribution(self, protocol_data: Dict, filename: Optional[str] = None):
        
        if not protocol_data:
            print("No protocol data to visualize")
            return
        
        protocols = list(protocol_data.keys())
        counts = list(protocol_data.values())
        
        plt.figure(figsize=(10, 8))
        plt.pie(counts, labels=protocols, autopct='%1.1f%%', startangle=90)
        plt.title('Protocol Distribution', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        
        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, 'protocol_distribution.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_top_ips(self, ip_data: List[tuple], top_n: int = 10, 
                    filename: Optional[str] = None):
        
        if not ip_data:
            print("No IP data to visualize")
            return
        
        top_ips = sorted(ip_data, key=lambda x: x[1], reverse=True)[:top_n]
        ips = [ip for ip, _ in top_ips]
        counts = [count for _, count in top_ips]
        
        plt.figure(figsize=(12, 6))
        plt.barh(ips, counts, color='steelblue')
        plt.xlabel('Packet Count', fontsize=12)
        plt.ylabel('IP Address', fontsize=12)
        plt.title(f'Top {top_n} IP Addresses by Traffic', fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, f'top_{top_n}_ips.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_port_activity(self, port_data: Dict, top_n: int = 20, 
                          filename: Optional[str] = None):
        
        if not port_data:
            print("No port data to visualize")
            return
        
        sorted_ports = sorted(port_data.items(), key=lambda x: x[1], reverse=True)[:top_n]
        ports = [str(port) for port, _ in sorted_ports]
        counts = [count for _, count in sorted_ports]
        
        plt.figure(figsize=(14, 6))
        plt.bar(ports, counts, color='coral')
        plt.xlabel('Port Number', fontsize=12)
        plt.ylabel('Packet Count', fontsize=12)
        plt.title(f'Top {top_n} Active Ports', fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, f'top_{top_n}_ports.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_flow_duration(self, flows: List[Dict], filename: Optional[str] = None):
        
        if not flows:
            print("No flow data to visualize")
            return
        
        durations = [f.get('duration', 0) for f in flows if f.get('duration', 0) > 0]
        
        if not durations:
            print("No valid duration data")
            return
        
        plt.figure(figsize=(12, 6))
        plt.hist(durations, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        plt.xlabel('Flow Duration (seconds)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Flow Duration Distribution', fontsize=16, fontweight='bold')
        plt.yscale('log')
        plt.tight_layout()
        
        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, 'flow_duration.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def plot_flow_size(self, flows: List[Dict], filename: Optional[str] = None):
        
        if not flows:
            print("No flow data to visualize")
            return
        
        sizes = [f.get('bytes', 0) for f in flows if f.get('bytes', 0) > 0]
        
        if not sizes:
            print("No valid size data")
            return
        
        plt.figure(figsize=(12, 6))
        plt.hist(sizes, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
        plt.xlabel('Flow Size (bytes)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Flow Size Distribution', fontsize=16, fontweight='bold')
        plt.yscale('log')
        plt.xscale('log')
        plt.tight_layout()
        
        if filename:
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300, bbox_inches='tight')
        else:
            plt.savefig(os.path.join(self.output_dir, 'flow_size.png'), 
                       dpi=300, bbox_inches='tight')
        
        plt.close()
    
    def create_dashboard(self, analysis_results: Dict, flows: Optional[List[Dict]] = None):
        
        fig = plt.figure(figsize=(20, 12))
        
                               
        if 'ip_traffic' in analysis_results:
            ax1 = plt.subplot(2, 3, 1)
            protocols = analysis_results['ip_traffic'].get('protocols', {})
            if protocols:
                self.plot_protocol_distribution(protocols, filename=None)
        
                        
        if 'ip_traffic' in analysis_results:
            ax2 = plt.subplot(2, 3, 2)
            top_ips = list(analysis_results['ip_traffic'].get('source_ips', {}).items())[:10]
            if top_ips:
                self.plot_top_ips(top_ips, top_n=10, filename=None)
        
                       
        if flows:
            ax3 = plt.subplot(2, 3, 3)
            self.plot_flow_duration(flows, filename=None)
        
        plt.suptitle('ForensiQ (Network) Security Dashboard', fontsize=20, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'dashboard.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Dashboard saved to {self.output_dir}/dashboard.png")

