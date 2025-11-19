# SpikeGuard Abbreviations & Glossary

| Term / Abbreviation | Full Form / Meaning | Notes |
|---------------------|---------------------|-------|
| GUI | Graphical User Interface | SpikeGuard offers a Tkinter-based GUI. |
| CLI | Command-Line Interface | SpikeGuard also ships with a CLI (`main.py`). |
| PCAP | Packet Capture | Standard file format for captured network packets. |
| BPF | Berkeley Packet Filter | Filtering syntax used to capture specific traffic. |
| TCP | Transmission Control Protocol | Reliable transport-layer protocol. |
| UDP | User Datagram Protocol | Connectionless transport-layer protocol. |
| ICMP | Internet Control Message Protocol | Used for diagnostics (e.g., ping). |
| DNS | Domain Name System | Resolves human-readable names to IP addresses. |
| HTTP | HyperText Transfer Protocol | Protocol for web communication. |
| IP | Internet Protocol | Network layer protocol for routing packets. |
| SYN | Synchronize | TCP flag used to initiate a connection. |
| ACK | Acknowledgement | TCP flag confirming receipt of packets. |
| DoS / DDoS | Denial of Service / Distributed Denial of Service | Flooding attacks that overwhelm targets. |
| IDS / IDPS | Intrusion Detection System / Intrusion Detection & Prevention System | Security systems monitoring for malicious activity. |
| C2 | Command and Control | Communication channel used by attackers to control compromised systems. |
| Npcap | Network Packet Capture Library | Required driver on Windows for live capture. |
| Scapy | Scapy Packet Manipulation Library | Python library used for packet capture/analysis. |
| PyInstaller | Python Installer | Tool used to build standalone `.exe` files. |
| RFC | Request for Comments | Official documents describing internet standards. |
| JSON | JavaScript Object Notation | Lightweight data-interchange format. |
| CSV | Comma-Separated Values | Tabular data format used for exports. |
| Tkinter | Tk Interface | Built-in Python library for GUI development. |
| Pandas | Python Data Analysis Library | Used for data manipulation/export. |
| Matplotlib / Seaborn | Python Visualization Libraries | Used for graphs and charts. |

## Hard / Domain-Specific Terms

| Term | Meaning / Explanation |
|------|-----------------------|
| Time-windowed analysis | Technique that evaluates network activity within fixed time windows to detect bursts or anomalies. |
| Rolling average baseline | Dynamic baseline calculation that adapts detection thresholds based on typical traffic volume. |
| Alert correlation | Combining related alerts to identify more complex attack patterns and reduce noise. |
| Stealth scan (FIN/XMAS/NULL) | Reconnaissance technique using unusual TCP flag combinations to evade detection. |
| Flow analysis | Tracking communication pairs (source/destination) to analyze connection behavior over time. |
| Threat intelligence | External data about known malicious IPs, domains, or signatures. |
| Packet sniffing | Capturing raw network packets for analysis. |
| Stateful tracking | Monitoring protocol state (e.g., TCP connection phases) to detect anomalies. |
| Baselining | Establishing normal behavior to identify deviations indicative of threats. |
| PCAP replay | Analyzing previously captured network traffic instead of live capture. |

> **Tip:** Add additional acronyms or field-specific terms to this file as the project grows.

