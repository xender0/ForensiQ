import click
import sys
from pathlib import Path
from forensics import (
    PacketCapture, ProtocolAnalyzer, FlowAnalyzer,
    IntrusionDetector, NetworkVisualizer, ReportGenerator
)
from colorama import init, Fore, Style

init(autoreset=True)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    pass


@cli.command()
@click.option('--interface', '-i', help='Network interface to capture on (use "auto" for auto-detection)')
@click.option('--output', '-o', default='capture.pcap', help='Output PCAP file')
@click.option('--filter', '-f', help='BPF filter string')
@click.option('--count', '-c', default=0, help='Number of packets to capture (0 for unlimited)')
@click.option('--duration', '-d', type=int, help='Capture duration in seconds')
def capture(interface, output, filter, count, duration):
    try:
        if not interface or interface.lower() == 'auto':
            print(f"{Fore.YELLOW}No interface specified. Detecting active interface...")
            active_iface = PacketCapture.get_active_interface()
            
            if active_iface:
                print(f"{Fore.GREEN}Auto-detected active interface: {active_iface}")
                use_auto = click.confirm('Use this interface?', default=True)
                if use_auto:
                    interface = active_iface
                else:
                    PacketCapture.list_interfaces()
                    interface = click.prompt('Enter interface name', type=str)
            else:
                print(f"{Fore.YELLOW}Could not auto-detect active interface. Listing all interfaces...")
                PacketCapture.list_interfaces()
                interface = click.prompt('Enter interface name', type=str)
        
        print(f"{Fore.GREEN}Starting packet capture...")
        print(f"{Fore.CYAN}Interface: {interface}")
        print(f"{Fore.CYAN}Output: {output}")
        if filter:
            print(f"{Fore.CYAN}Filter: {filter}")
        
        capture = PacketCapture(
            interface=interface,
            output_file=output,
            filter=filter,
            count=count if count > 0 else 0
        )
        
        capture.start(duration=duration)
        
        import time
        try:
            while capture.is_capturing:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Stopping capture...")
            capture.stop()
        
        stats = capture.get_statistics()
        print(f"\n{Fore.GREEN}Capture complete!")
        print(f"{Fore.CYAN}Total packets: {stats['total_packets']}")
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('pcap_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='analysis_output', help='Output directory')
def analyze(pcap_file, output_dir):
    try:
        print(f"{Fore.GREEN}Starting analysis of {pcap_file}...")
        
        Path(output_dir).mkdir(exist_ok=True)
        
        print(f"{Fore.CYAN}Running protocol analysis...")
        analyzer = ProtocolAnalyzer(pcap_file)
        analysis_results = analyzer.analyze()
        
        print(f"{Fore.CYAN}Extracting network flows...")
        flow_analyzer = FlowAnalyzer(pcap_file)
        flows = flow_analyzer.extract_flows()
        flow_stats = flow_analyzer.get_flow_statistics()
        
        print(f"{Fore.CYAN}Running intrusion detection...")
        detector = IntrusionDetector(pcap_file)
        threats = detector.detect_anomalies()
        threat_summary = detector.get_threat_summary()
        
        print(f"{Fore.CYAN}Generating visualizations...")
        visualizer = NetworkVisualizer(output_dir=output_dir)
        
        if 'ip_traffic' in analysis_results:
            ip_traffic = analysis_results['ip_traffic']
            if 'protocols' in ip_traffic:
                visualizer.plot_protocol_distribution(ip_traffic['protocols'])
            
            top_ips = analyzer.get_top_ips(10)
            if top_ips['top_sources']:
                visualizer.plot_top_ips(top_ips['top_sources'], top_n=10)
        
        if flows:
            visualizer.plot_flow_duration(flows)
            visualizer.plot_flow_size(flows)
        
        print(f"{Fore.CYAN}Generating reports...")
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
        
        print(f"\n{Fore.GREEN}Analysis complete!")
        print(f"{Fore.CYAN}Reports saved to: {output_dir}")
        print(f"{Fore.CYAN}  - HTML: {html_report}")
        print(f"{Fore.CYAN}  - JSON: {json_report}")
        print(f"{Fore.CYAN}  - Text: {text_report}")
        print(f"\n{Fore.YELLOW}Summary:")
        print(f"  Packets: {len(analyzer.packets)}")
        print(f"  Flows: {len(flows)}")
        print(f"  Threats: {threat_summary['total_threats']}")
        print(f"  Anomalies: {threat_summary['total_anomalies']}")
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('pcap_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='flows.csv', help='Output CSV file')
def flows(pcap_file, output):
    try:
        print(f"{Fore.GREEN}Extracting flows from {pcap_file}...")
        
        flow_analyzer = FlowAnalyzer(pcap_file)
        flows = flow_analyzer.extract_flows()
        stats = flow_analyzer.get_flow_statistics()
        
        print(f"{Fore.CYAN}Found {len(flows)} flows")
        print(f"{Fore.CYAN}Total packets: {stats['total_packets']}")
        print(f"{Fore.CYAN}Total bytes: {stats['total_bytes']:,}")
        
        flow_analyzer.export_to_csv(output)
        print(f"{Fore.GREEN}Flows exported to {output}")
        
        suspicious = flow_analyzer.find_suspicious_flows()
        if suspicious:
            print(f"\n{Fore.YELLOW}Found {len(suspicious)} suspicious flows:")
            for flow in suspicious[:5]:
                print(f"  {flow['src_ip']}:{flow['src_port']} -> {flow['dst_ip']}:{flow['dst_port']}")
                print(f"    Reasons: {', '.join(flow.get('suspicious_reasons', []))}")
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('pcap_file', type=click.Path(exists=True))
def detect(pcap_file):
    try:
        print(f"{Fore.GREEN}Running intrusion detection on {pcap_file}...")
        
        detector = IntrusionDetector(pcap_file)
        threats = detector.detect_anomalies()
        summary = detector.get_threat_summary()
        
        print(f"\n{Fore.CYAN}Detection Results:")
        print(f"  Threats: {summary['total_threats']}")
        print(f"  Anomalies: {summary['total_anomalies']}")
        print(f"  Unique Source IPs: {summary['unique_source_ips']}")
        
        if threats:
            print(f"\n{Fore.YELLOW}Threats Detected:")
            for i, threat in enumerate(threats[:10], 1):
                severity_color = {
                    'High': Fore.RED,
                    'Medium': Fore.YELLOW,
                    'Low': Fore.CYAN
                }.get(threat.get('severity', 'Low'), Fore.WHITE)
                
                print(f"{severity_color}  {i}. [{threat.get('severity', 'N/A')}] {threat.get('type', 'Unknown')}")
                print(f"     {threat.get('description', '')}")
        
        alert_report = detector.generate_alert_report()
        print(f"\n{Fore.CYAN}Alert Report:")
        print(alert_report)
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        sys.exit(1)


@cli.command()
def interfaces():
    try:
        PacketCapture.list_interfaces()
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()

