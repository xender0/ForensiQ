# SpikeGuard

SpikeGuard is an advanced network security analysis and threat detection platform for analyzing network traffic, detecting anomalies, and generating comprehensive security reports. Designed for enterprise network security analysis, incident response, and digital forensics investigations.

## Features

- **GUI Interface**: Modern graphical user interface for easy interaction with all tools
- **Packet Capture**: Live and offline packet capture using multiple interfaces
- **Protocol Analysis**: Deep inspection of HTTP, DNS, TCP, UDP, and other protocols
- **Flow Analysis**: Network flow tracking and connection analysis
- **Intrusion Detection**: Advanced anomaly detection with time-windowed analysis, stealth scan detection, and alert correlation
- **Traffic Visualization**: Graphical representation of network data
- **Forensic Reporting**: Automated report generation in HTML, JSON, and text formats

## Requirements

- Python 3.8+
- Administrator/root privileges for packet capture (or use existing PCAP files)
- Network interface access (for live capture)
- **GUI**: tkinter (usually included with Python; on Linux may need: `sudo apt-get install python3-tk`)
- **Windows**: Npcap or WinPcap for live packet capture (see Windows Setup section)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd spikeguard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For packet capture on Linux, set capabilities:
```bash
sudo setcap cap_net_raw+eip $(readlink -f $(which python3))
```

## Quick Start

### Using the GUI (Recommended)

The easiest way to use SpikeGuard is through the graphical interface:

```bash
python gui.py
```

The GUI provides:
- **Packet Capture Tab**: Live packet capture with real-time statistics
- **PCAP Analysis Tab**: Comprehensive analysis with protocol details
- **Flow Analysis Tab**: Network flow extraction and visualization
- **Intrusion Detection Tab**: Security threat detection and reporting
- **Visualization Tab**: Generate charts and graphs from network data
- **Reports Tab**: Generate comprehensive forensic reports

### Using the Command Line

#### List Network Interfaces
```bash
python main.py interfaces
```

#### Capture Network Traffic
```bash
# Auto-detect active interface (recommended)
python main.py capture -i auto -o capture.pcap -c 100

# Capture with filter and duration
python main.py capture -i auto -f "tcp port 80" -d 60

# Windows: Use interface name from interfaces command
python main.py capture -i "\Device\NPF_{...}" -o capture.pcap
```

#### Analyze PCAP File
```bash
# Full analysis with reports and visualizations
python main.py analyze capture.pcap -o analysis_output
```

#### Extract Network Flows
```bash
python main.py flows capture.pcap -o flows.csv
```

#### Run Intrusion Detection
```bash
python main.py detect capture.pcap
```

## Usage Examples

### Python API

#### Basic Packet Capture
```python
from forensics import PacketCapture

# Auto-detect active interface
active_iface = PacketCapture.get_active_interface()
capture = PacketCapture(interface=active_iface, output_file='capture.pcap')
capture.start(duration=60)  # Capture for 60 seconds
```

#### Protocol Analysis
```python
from forensics import ProtocolAnalyzer

analyzer = ProtocolAnalyzer('capture.pcap')
results = analyzer.analyze()
top_ips = analyzer.get_top_ips(10)
```

#### Flow Analysis
```python
from forensics import FlowAnalyzer

flow_analyzer = FlowAnalyzer('capture.pcap')
flows = flow_analyzer.extract_flows()
suspicious = flow_analyzer.find_suspicious_flows()
flow_analyzer.export_to_csv('flows.csv')
```

#### Intrusion Detection
```python
from forensics import IntrusionDetector

# Basic usage
detector = IntrusionDetector('capture.pcap')
threats = detector.detect_anomalies()
print(detector.generate_alert_report())

# With custom configuration
config = {
    'port_scan_ports_threshold': 30,
    'port_scan_time_window': 30,
    'syn_flood_count': 50,
}
detector = IntrusionDetector('capture.pcap', config=config)
threats = detector.detect_anomalies()

# Load threat intelligence
detector.load_malicious_ips_from_file('malicious_ips.txt')
```

#### Generate Reports
```python
from forensics import ReportGenerator, ProtocolAnalyzer, FlowAnalyzer, IntrusionDetector

# Run analysis
analyzer = ProtocolAnalyzer('capture.pcap')
analysis_results = analyzer.analyze()

flow_analyzer = FlowAnalyzer('capture.pcap')
flows = flow_analyzer.extract_flows()

detector = IntrusionDetector('capture.pcap')
threats = detector.detect_anomalies()

# Generate reports
report_gen = ReportGenerator(output_dir='reports')
report_data = {
    'summary': {
        'total_packets': len(analyzer.packets),
        'total_flows': len(flows),
        'total_threats': len(detector.threats),
    },
    'ip_traffic': analysis_results.get('ip_traffic', {}),
    'threats': detector.threats,
    'anomalies': detector.anomalies,
}

report_gen.generate_html_report(report_data)
report_gen.generate_json_report(report_data)
```

## Windows Setup

### Live Packet Capture on Windows

**Important**: Live packet capture on Windows requires Npcap or WinPcap:

1. **Install Npcap** (recommended):
   - Download from: https://nmap.org/npcap/
   - Install with "WinPcap API-compatible Mode" enabled
   - Run as Administrator if needed

2. **Alternative**: Use WSL2 (Windows Subsystem for Linux) for Linux-like packet capture

### Working Without Live Capture

You can use SpikeGuard effectively without live capture:

1. **Capture packets with Wireshark** and save as PCAP
2. **Analyze PCAP files** - all analysis features work:
   ```bash
   python main.py analyze capture.pcap -o results
   ```

### Troubleshooting Windows Issues

- **"No libpcap provider available"**: Install Npcap or use PCAP file analysis only
- **"Permission denied"**: Run as Administrator or install Npcap with admin privileges
- **Interface names**: Windows uses names like `\Device\NPF_{...}` - use `python main.py interfaces` to list them
- **Auto-detect**: Use `-i auto` to automatically detect and use the active interface

## Testing

### Quick Test with Generated Traffic

```bash
# Generate test traffic with various attack types
python examples/generate_test_traffic.py --output test.pcap --duration 60

# Run intrusion detection
python main.py detect test.pcap

# Or use the test script
python examples/test_intrusion_detection.py test.pcap
```

Expected detections:
- ✅ Port Scan (High severity)
- ✅ Potential SYN Flood (High severity)
- ✅ Stealth Port Scan (High severity)
- ✅ ICMP Anomaly (Medium severity)
- ✅ DNS Anomaly (Medium severity)

### Test with Public Datasets

#### CICIDS2017 (Recommended)
- **Download**: https://www.unb.ca/cic/datasets/ids-2017.html
- **Size**: ~3 GB
- **Usage**:
  ```bash
  python main.py detect CICIDS2017/Monday-WorkingHours.pcap
  ```

#### Other Datasets
- **UNSW-NB15**: https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/ADFA-NB15-Datasets/
- **CTU-13**: https://www.stratosphereips.org/datasets-ctu13
- **NSL-KDD**: https://www.unb.ca/cic/datasets/nsl.html

### Running Tests

```bash
# Run test suite
python -m pytest tests/ -v

# Run specific test
python tests/test_forensics.py
```

## Detection Capabilities

### High Severity Threats
- **Port Scans**: Time-windowed detection (>50 ports in 60 seconds)
- **Stealth Scans**: FIN, XMAS, NULL scan detection
- **Flood Attacks**: DoS/DDoS with rolling average baselines
- **SYN Floods**: Time-windowed with SYN/ACK ratio analysis
- **Known Malicious IPs**: Threat intelligence integration
- **Established C2 Channels**: Correlated alerts (Suspicious Port + Malicious IP)

### Medium Severity Anomalies
- **ICMP Anomalies**: Type-specific detection (ping floods, network mapping)
- **DNS Anomalies**: NXDOMAIN rate, unusual query types, DNS tunneling
- **Suspicious Ports**: Connections to known backdoor ports
- **Unusual Port Usage**: Long-term multi-port activity

### Low Severity Anomalies
- **Unusual TCP Flags**: Malformed packet detection
- **Out-of-State Packets**: TCP connection state violations

### Key Features
- **Time-Windowed Analysis**: All detections use configurable time windows to reduce false positives
- **Rolling Averages**: Adaptive thresholds based on network baselines
- **Stateful TCP Tracking**: Monitors connection states for anomaly detection
- **Alert Correlation**: Combines related alerts for complex attack detection
- **Configurable Thresholds**: Adaptable to different network environments

## Project Structure

```
spikeguard/
├── forensics/
│   ├── __init__.py
│   ├── packet_capture.py      # Packet capture functionality
│   ├── protocol_analyzer.py   # Protocol analysis
│   ├── flow_analyzer.py        # Network flow analysis
│   ├── intrusion_detector.py  # Anomaly and threat detection
│   ├── visualizer.py          # Data visualization
│   └── report_generator.py    # Forensic report generation
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Utility functions
├── examples/
│   ├── basic_capture.py
│   ├── analyze_pcap.py
│   ├── full_analysis.py
│   ├── generate_test_traffic.py
│   └── test_intrusion_detection.py
├── tests/
│   └── test_forensics.py
├── requirements.txt
├── README.md
├── main.py                     # CLI interface
├── gui.py                      # GUI application
└── run_gui.py                  # GUI launcher script
```

## Modules

### Packet Capture
Captures network packets from live interfaces or analyzes existing PCAP files. Supports BPF filters, packet count limits, and duration-based capture.

### Protocol Analyzer
Extracts and analyzes protocol-specific information from network traffic including HTTP, DNS, TCP, UDP, and ICMP.

### Flow Analyzer
Tracks network connections and analyzes communication patterns. Identifies suspicious flows and exports data to CSV.

### Intrusion Detector
Identifies suspicious activities, anomalies, and potential security threats using time-windowed analysis, statistical baselines, and pattern recognition.

### Visualizer
Creates visual representations of network data including protocol distributions, top IPs, and flow analysis charts.

### Report Generator
Generates comprehensive forensic reports in multiple formats (HTML, JSON, text) with detailed findings and evidence.

## Troubleshooting

### Permission Denied
- **Linux/Mac**: Use `sudo` or set capabilities: `sudo setcap cap_net_raw+eip $(readlink -f $(which python3))`
- **Windows**: Run as Administrator or install Npcap

### No Packets Captured
- Check interface name is correct (`python main.py interfaces`)
- Verify network interface is active
- Check firewall settings
- Use `-i auto` to auto-detect active interface

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher
- Check virtual environment is activated

### No Threats Detected
- Verify PCAP file is valid: `python -c "from scapy.all import rdpcap; p=rdpcap('test.pcap'); print(f'{len(p)} packets')"`
- Use lower thresholds for testing (see configuration examples)
- Check that test traffic contains attack patterns

### Too Many False Positives
- Adjust thresholds in configuration (use higher values)
- Tune time windows for your network environment
- Review and whitelist legitimate traffic patterns

### Performance Issues
- Use smaller time windows for testing
- Process large files in chunks
- Use BPF filters to reduce packet count

## Example Scripts

Run example scripts in the `examples/` directory:

```bash
# Basic capture example
python examples/basic_capture.py

# Analyze PCAP file
python examples/analyze_pcap.py capture.pcap

# Full forensic analysis
python examples/full_analysis.py capture.pcap output_dir

# Generate test traffic
python examples/generate_test_traffic.py --output test.pcap --duration 60

# Test intrusion detection
python examples/test_intrusion_detection.py test.pcap
```

## Output Files

- **PCAP files**: Captured network packets
- **CSV files**: Exported flow and protocol data
- **HTML reports**: Interactive forensic reports with visualizations
- **JSON reports**: Machine-readable analysis data
- **PNG files**: Network traffic visualizations (protocol distribution, top IPs, flow charts)
- **Text reports**: Human-readable summary reports

## Building Executable (.exe)

To create a standalone Windows executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   python build_exe.py
   ```

3. Find the executable in `dist/SpikeGuard.exe`

For detailed instructions, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) or [QUICK_BUILD_GUIDE.md](QUICK_BUILD_GUIDE.md)

**Note**: The executable is standalone (no Python required), but users still need Npcap installed for live packet capture on Windows.

## License

MIT License

## Developers

- Manish Kumar
- Mohit Kalwar
- Mukul Dev
- Tanish Dhingra

**Mentored under Dr. Pramod Maurya**
