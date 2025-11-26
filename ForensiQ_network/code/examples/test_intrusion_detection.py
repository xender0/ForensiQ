

import sys
import time
from pathlib import Path
from forensics import IntrusionDetector

def test_detection(pcap_file: str, config: dict = None):
    
    print(f"\n{'='*60}")
    print(f"Testing Intrusion Detection: {pcap_file}")
    print(f"{'='*60}\n")
    
    if not Path(pcap_file).exists():
        print(f"ERROR: File not found: {pcap_file}")
        return False
    
    try:
        start_time = time.time()
        
                             
        detector = IntrusionDetector(pcap_file, config=config)
        
                                           
        malicious_ips_file = Path('malicious_ips.txt')
        if malicious_ips_file.exists():
            detector.load_malicious_ips_from_file(str(malicious_ips_file))
            print(f"Loaded {len(detector.known_malicious_ips)} malicious IPs")
        
                       
        threats = detector.detect_anomalies()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
                     
        summary = detector.get_threat_summary()
        
                       
        print(f"\n{'='*60}")
        print("DETECTION RESULTS")
        print(f"{'='*60}")
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"Total Packets: {len(detector.packets)}")
        print(f"Packets/Second: {len(detector.packets)/processing_time:.0f}")
        print(f"\nThreats Detected: {summary['total_threats']}")
        print(f"Anomalies Detected: {summary['total_anomalies']}")
        print(f"Unique Source IPs: {summary['unique_source_ips']}")
        
        if summary['threat_types']:
            print(f"\nThreat Types:")
            for threat_type, count in summary['threat_types'].items():
                print(f"  - {threat_type}: {count}")
        
        if summary['anomaly_types']:
            print(f"\nAnomaly Types:")
            for anomaly_type, count in summary['anomaly_types'].items():
                print(f"  - {anomaly_type}: {count}")
        
        if summary['severity_breakdown']:
            print(f"\nSeverity Breakdown:")
            for severity, count in summary['severity_breakdown'].items():
                print(f"  - {severity}: {count}")
        
                               
        print(f"\n{'='*60}")
        print("DETAILED ALERT REPORT")
        print(f"{'='*60}")
        report = detector.generate_alert_report()
        print(report)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_configs(pcap_file: str):
    
    print(f"\n{'='*60}")
    print("Testing with Different Configurations")
    print(f"{'='*60}\n")
    
    configs = {
        'Default': None,
        'Sensitive (Lower Thresholds)': {
            'port_scan_ports_threshold': 20,
            'port_scan_time_window': 30,
            'syn_flood_count': 50,
            'syn_flood_time_window': 3,
        },
        'Relaxed (Higher Thresholds)': {
            'port_scan_ports_threshold': 100,
            'port_scan_time_window': 120,
            'syn_flood_count': 200,
            'syn_flood_time_window': 10,
            'flood_multiplier': 20,
        }
    }
    
    for config_name, config in configs.items():
        print(f"\n{'-'*60}")
        print(f"Configuration: {config_name}")
        print(f"{'-'*60}")
        test_detection(pcap_file, config)


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_intrusion_detection.py <pcap_file> [--configs]")
        print("\nExample:")
        print("  python test_intrusion_detection.py test_traffic.pcap")
        print("  python test_intrusion_detection.py test_traffic.pcap --configs")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    test_configs = '--configs' in sys.argv
    
    if test_configs:
        test_with_configs(pcap_file)
    else:
        test_detection(pcap_file)


if __name__ == '__main__':
    main()

