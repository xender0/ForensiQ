

from forensics import ProtocolAnalyzer, FlowAnalyzer, IntrusionDetector
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_pcap.py <pcap_file>")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    
    print(f"Analyzing {pcap_file}...")
    
                       
    print("\n1. Protocol Analysis")
    analyzer = ProtocolAnalyzer(pcap_file)
    results = analyzer.analyze()
    
                   
    top_ips = analyzer.get_top_ips(5)
    print("\nTop 5 Source IPs:")
    for ip, count in top_ips['top_sources']:
        print(f"  {ip}: {count} packets")
    
                   
    print("\n2. Flow Analysis")
    flow_analyzer = FlowAnalyzer(pcap_file)
    flows = flow_analyzer.extract_flows()
    stats = flow_analyzer.get_flow_statistics()
    
    print(f"Total flows: {stats['total_flows']}")
    print(f"Total packets: {stats['total_packets']}")
    print(f"Total bytes: {stats['total_bytes']:,}")
    
                         
    print("\n3. Intrusion Detection")
    detector = IntrusionDetector(pcap_file)
    threats = detector.detect_anomalies()
    summary = detector.get_threat_summary()
    
    print(f"Threats detected: {summary['total_threats']}")
    print(f"Anomalies found: {summary['total_anomalies']}")
    
    if threats:
        print("\nTop Threats:")
        for threat in threats[:5]:
            print(f"  [{threat['severity']}] {threat['type']}")
            print(f"    {threat['description']}")
    
                     
    print("\n4. Generating Report")
    report = analyzer.generate_report()
    print(report)

if __name__ == '__main__':
    main()

