

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Template


class ReportGenerator:
    
    
    def __init__(self, output_dir: str = "reports"):
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_html_report(self, analysis_data: Dict, filename: Optional[str] = None) -> str:
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"forensic_report_{timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        html_template = 
        
        template = Template(html_template)
        
                                   
        report_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'summary': analysis_data.get('summary', {}),
            'ip_traffic': analysis_data.get('ip_traffic', {}),
            'threats': analysis_data.get('threats', []),
            'anomalies': analysis_data.get('anomalies', []),
            'http_traffic': analysis_data.get('http_traffic', {}),
            'dns_traffic': analysis_data.get('dns_traffic', {})
        }
        
                                  
        if 'ip_traffic' in analysis_data and 'source_ips' in analysis_data['ip_traffic']:
            top_sources = sorted(analysis_data['ip_traffic']['source_ips'].items(), 
                               key=lambda x: x[1], reverse=True)[:10]
            report_data['ip_traffic']['top_sources'] = top_sources
        
        html_content = template.render(**report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report generated: {filepath}")
        return filepath
    
    def generate_json_report(self, analysis_data: Dict, filename: Optional[str] = None) -> str:
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"forensic_report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"JSON report generated: {filepath}")
        return filepath
    
    def generate_text_report(self, analysis_data: Dict, filename: Optional[str] = None) -> str:
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"forensic_report_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        lines = []
        lines.append("=" * 80)
        lines.append("FORENSIQ (NETWORK) SECURITY REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
                 
        if 'summary' in analysis_data:
            summary = analysis_data['summary']
            lines.append("EXECUTIVE SUMMARY")
            lines.append("-" * 80)
            lines.append(f"Total Packets: {summary.get('total_packets', 0)}")
            lines.append(f"Total Flows: {summary.get('total_flows', 0)}")
            lines.append(f"Threats Detected: {summary.get('total_threats', 0)}")
            lines.append(f"Anomalies Found: {summary.get('total_anomalies', 0)}")
            lines.append("")
        
                    
        if 'ip_traffic' in analysis_data:
            ip = analysis_data['ip_traffic']
            lines.append("IP TRAFFIC ANALYSIS")
            lines.append("-" * 80)
            lines.append(f"IP Packets: {ip.get('ip_packets', 0)}")
            lines.append(f"Total Bytes: {ip.get('total_bytes', 0):,}")
            lines.append("")
        
                 
        if 'threats' in analysis_data:
            lines.append("SECURITY THREATS")
            lines.append("-" * 80)
            for i, threat in enumerate(analysis_data['threats'], 1):
                lines.append(f"{i}. [{threat.get('severity', 'N/A')}] {threat.get('type', 'Unknown')}")
                lines.append(f"   Source: {threat.get('source_ip', 'N/A')}")
                lines.append(f"   {threat.get('description', '')}")
                lines.append("")
        
                   
        if 'anomalies' in analysis_data:
            lines.append("ANOMALIES")
            lines.append("-" * 80)
            for i, anomaly in enumerate(analysis_data['anomalies'], 1):
                lines.append(f"{i}. [{anomaly.get('severity', 'N/A')}] {anomaly.get('type', 'Unknown')}")
                lines.append(f"   Source: {anomaly.get('source_ip', 'N/A')}")
                lines.append(f"   {anomaly.get('description', '')}")
                lines.append("")
        
        lines.append("=" * 80)
        lines.append("End of Report")
        lines.append("=" * 80)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"Text report generated: {filepath}")
        return filepath

