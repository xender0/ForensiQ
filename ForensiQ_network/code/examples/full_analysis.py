

from forensics import (
    ProtocolAnalyzer, FlowAnalyzer, IntrusionDetector,
    NetworkVisualizer, ReportGenerator
)
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python full_analysis.py <pcap_file> [output_dir]")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'forensic_analysis'
    
                             
    Path(output_dir).mkdir(exist_ok=True)
    
    print(f"Starting full forensic analysis of {pcap_file}...")
    print(f"Output directory: {output_dir}\n")
    
                          
    print("=" * 60)
    print("STEP 1: Protocol Analysis")
    print("=" * 60)
    analyzer = ProtocolAnalyzer(pcap_file)
    analysis_results = analyzer.analyze()
    print("✓ Protocol analysis complete\n")
    
                      
    print("=" * 60)
    print("STEP 2: Flow Analysis")
    print("=" * 60)
    flow_analyzer = FlowAnalyzer(pcap_file)
    flows = flow_analyzer.extract_flows()
    flow_stats = flow_analyzer.get_flow_statistics()
    print(f"✓ Extracted {len(flows)} flows\n")
    
                            
    print("=" * 60)
    print("STEP 3: Intrusion Detection")
    print("=" * 60)
    detector = IntrusionDetector(pcap_file)
    threats = detector.detect_anomalies()
    threat_summary = detector.get_threat_summary()
    print(f"✓ Detected {threat_summary['total_threats']} threats and "
          f"{threat_summary['total_anomalies']} anomalies\n")
    
                      
    print("=" * 60)
    print("STEP 4: Generating Visualizations")
    print("=" * 60)
    visualizer = NetworkVisualizer(output_dir=output_dir)
    
                       
    visualizer.plot_traffic_over_time(analyzer.packets)
    
                           
    if 'ip_traffic' in analysis_results and 'protocols' in analysis_results['ip_traffic']:
        visualizer.plot_protocol_distribution(analysis_results['ip_traffic']['protocols'])
    
             
    top_ips = analyzer.get_top_ips(10)
    if top_ips['top_sources']:
        visualizer.plot_top_ips(top_ips['top_sources'], top_n=10)
    
                         
    if flows:
        visualizer.plot_flow_duration(flows)
        visualizer.plot_flow_size(flows)
    
    print("✓ Visualizations generated\n")
    
                          
    print("=" * 60)
    print("STEP 5: Generating Reports")
    print("=" * 60)
    report_gen = ReportGenerator(output_dir=output_dir)
    
    report_data = {
        'summary': {
            'total_packets': len(analyzer.packets),
            'total_flows': len(flows),
            'total_threats': threat_summary['total_threats'],
            'total_anomalies': threat_summary['total_anomalies']
        },
        'ip_traffic': analysis_results.get('ip_traffic', {}),
        'threats': detector.threats,
        'anomalies': detector.anomalies,
        'http_traffic': analysis_results.get('http_traffic', {}),
        'dns_traffic': analysis_results.get('dns_traffic', {})
    }
    
    html_report = report_gen.generate_html_report(report_data)
    json_report = report_gen.generate_json_report(report_data)
    text_report = report_gen.generate_text_report(report_data)
    
    print("✓ Reports generated\n")
    
             
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Total Packets: {len(analyzer.packets):,}")
    print(f"  Network Flows: {len(flows):,}")
    print(f"  Threats Detected: {threat_summary['total_threats']}")
    print(f"  Anomalies Found: {threat_summary['total_anomalies']}")
    print(f"\nOutput Files:")
    print(f"  HTML Report: {html_report}")
    print(f"  JSON Report: {json_report}")
    print(f"  Text Report: {text_report}")
    print(f"  Visualizations: {output_dir}/")

if __name__ == '__main__':
    main()

