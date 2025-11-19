# SpikeGuard - Explained Simply (ELI5)

## What is SpikeGuard?

Imagine your computer network is like a busy highway. Cars (data packets) are constantly traveling back and forth between different places (computers). SpikeGuard is like having a **super-smart traffic inspector** that can:

1. **Watch** all the cars on the highway (capture network traffic)
2. **Understand** what each car is doing (analyze protocols)
3. **Track** conversations between different places (flow analysis)
4. **Spot** suspicious or dangerous behavior (intrusion detection)
5. **Create reports** with pictures and charts (visualization and reporting)

Think of it as a detective tool for computer networks!

---

## The Big Picture: What Does It Do?

When someone uses your network (or attacks it), they leave behind digital footprints. This toolkit helps you:

- **Capture** network traffic (like recording a phone conversation)
- **Analyze** what happened (like reading a transcript)
- **Detect** bad guys (like spotting suspicious behavior)
- **Report** findings (like writing a police report)

---

## The Main Components (The Building Blocks)

### 1. **Packet Capture** (`packet_capture.py`)
**What it does:** Like a security camera that records everything happening on your network.

**In simple terms:**
- It watches your network connection (like Wi-Fi or Ethernet)
- It captures every piece of data that goes through
- It saves everything to a file (like recording a video)
- You can filter what to capture (like "only record cars going faster than 60 mph")

**Real-world example:** If someone visits a website, this captures all the data exchanged between their computer and the website.

---

### 2. **Protocol Analyzer** (`protocol_analyzer.py`)
**What it does:** Like a translator that understands different "languages" computers speak.

**In simple terms:**
- Computers talk to each other using different "languages" called protocols:
  - **HTTP:** For websites (like when you visit google.com)
  - **DNS:** For finding addresses (like asking "where is google.com?")
  - **TCP/UDP:** For sending data reliably or quickly
  - **ICMP:** For checking if something is reachable (like pinging)
- This tool reads captured traffic and tells you:
  - What websites were visited
  - What files were downloaded
  - Who talked to whom
  - How much data was transferred

**Real-world example:** It can tell you "Someone visited facebook.com 50 times and downloaded 2GB of data."

---

### 3. **Flow Analyzer** (`flow_analyzer.py`)
**What it does:** Like tracking a conversation between two people.

**In simple terms:**
- A "flow" is like a phone call between two computers
- It tracks:
  - Who called whom (source → destination)
  - How long they talked (duration)
  - How much they said (data transferred)
  - What they talked about (protocol used)
- It can spot suspicious conversations:
  - Very short calls to many different places (port scanning)
  - Huge data transfers (data exfiltration)
  - Unusual patterns (attacks)

**Real-world example:** "Computer A talked to 100 different computers in 1 minute - that's suspicious!"

---

### 4. **Intrusion Detector** (`intrusion_detector.py`)
**What it does:** Like a security guard that knows all the tricks bad guys use.

**In simple terms:**
This is the **smartest** part! It looks for patterns that indicate attacks:

#### Types of Threats It Detects:

**High Severity (Dangerous!):**
- **Port Scans:** Like someone checking all doors in a building to find unlocked ones
  - "This IP tried to connect to 50 different ports in 1 minute!"
- **Stealth Scans:** Sneaky ways to scan without being noticed
  - FIN scans, XMAS scans, NULL scans (like trying doors quietly)
- **Flood Attacks:** Overwhelming a server with too many requests
  - "Someone sent 1000 requests per second - that's a DoS attack!"
- **SYN Floods:** A specific type of attack that fills up connection queues
  - "Too many half-open connections - server is being attacked!"
- **Known Malicious IPs:** Connections to/from known bad actors
  - "This IP is on the FBI's watchlist!"

**Medium Severity (Suspicious):**
- **ICMP Anomalies:** Unusual ping patterns
  - "Someone is pinging way too much - might be mapping the network"
- **DNS Anomalies:** Weird domain name lookups
  - "Too many failed DNS queries - might be data exfiltration"
- **Suspicious Ports:** Connections to known backdoor ports
  - "Someone connected to port 4444 - that's a common hacker port!"

**Low Severity (Unusual but maybe okay):**
- **Unusual TCP Flags:** Weird packet configurations
- **Out-of-State Packets:** Packets that don't make sense in context

**How It Works:**
- Uses **time windows** (like "check what happened in the last 60 seconds")
- Uses **baselines** (like "normally we see 10 requests/second, but now it's 1000!")
- **Correlates** multiple alerts (like "port scan + malicious IP = likely attack")

---

### 5. **Visualizer** (`visualizer.py`)
**What it does:** Like creating charts and graphs to make data easy to understand.

**In simple terms:**
- Takes all the boring numbers and makes pretty pictures:
  - Pie charts showing protocol distribution
  - Bar charts showing top IP addresses
  - Histograms showing flow durations
  - Line graphs showing traffic over time
- Makes it easy to spot patterns visually

**Real-world example:** Instead of reading "TCP: 1000, UDP: 500, ICMP: 100", you see a pie chart that instantly shows TCP is the biggest slice.

---

### 6. **Report Generator** (`report_generator.py`)
**What it does:** Like writing a comprehensive report with all findings.

**In simple terms:**
- Combines everything into readable reports:
  - **HTML reports:** Pretty web pages with colors and formatting
  - **JSON reports:** Machine-readable data (for other programs)
  - **Text reports:** Simple text files (for reading)
- Includes:
  - Summary of findings
  - List of threats detected
  - Statistics and numbers
  - Evidence and proof

**Real-world example:** Like a police report that says "We found 5 suspicious activities, here's the evidence, here are the charts."

---

## How Everything Works Together

Think of it like a **detective investigation**:

1. **Packet Capture** = Gathering evidence (recording everything)
2. **Protocol Analyzer** = Understanding the evidence (what happened?)
3. **Flow Analyzer** = Tracking relationships (who talked to whom?)
4. **Intrusion Detector** = Finding crimes (what's suspicious?)
5. **Visualizer** = Making it visual (charts and graphs)
6. **Report Generator** = Writing the final report (presenting findings)

---

## The Two Ways to Use It

### 1. **Command Line Interface (CLI)** - `main.py`
**Like typing commands:**
```bash
python main.py capture -i auto -o capture.pcap
python main.py analyze capture.pcap
python main.py detect capture.pcap
```

**When to use:** When you're comfortable with typing commands, or when automating things.

### 2. **Graphical User Interface (GUI)** - `gui.py`
**Like using a smartphone app:**
- Click buttons
- Select files
- See results in windows
- No typing needed!

**When to use:** When you want an easy, visual way to use the tool.

---

## Real-World Use Cases

### Scenario 1: "Is My Network Being Attacked?"
1. Capture network traffic for 1 hour
2. Run intrusion detection
3. Get a report showing: "Found 3 port scans and 1 flood attack from IP 192.168.1.100"

### Scenario 2: "What Websites Are My Employees Visiting?"
1. Analyze captured traffic
2. Protocol analyzer extracts all HTTP requests
3. See list: "facebook.com (50 visits), youtube.com (30 visits), etc."

### Scenario 3: "Someone Stole Data - Find Evidence!"
1. Analyze traffic from the time of theft
2. Flow analyzer finds large data transfers
3. Report shows: "Computer A sent 10GB to external IP B at 2am"

### Scenario 4: "Is There Malware on My Network?"
1. Load list of known malicious IPs
2. Intrusion detector checks all connections
3. Finds: "Computer C connected to known malware server at IP X"

---

## Key Features Explained Simply

### Time-Windowed Analysis
**What it means:** Instead of looking at ALL traffic at once, it looks at small chunks of time (like 60-second windows).

**Why it matters:** A port scan happens quickly (in seconds), not over hours. This catches fast attacks!

**Example:** "In the 60-second window starting at 2:00 PM, IP X scanned 50 ports" ← This is suspicious!

### Rolling Averages
**What it means:** It learns what's "normal" for your network, then flags things that are way above normal.

**Why it matters:** Your network might normally have 100 requests/second. If suddenly it's 10,000/second, that's suspicious!

**Example:** "Normal: 100 requests/sec. Current: 10,000 requests/sec. That's 100x normal - FLAG IT!"

### Alert Correlation
**What it means:** When multiple suspicious things happen together, it creates a higher-severity alert.

**Why it matters:** One suspicious thing might be a mistake. Multiple suspicious things together = likely attack.

**Example:** "Port scan + malicious IP + suspicious port = CRITICAL: Likely C2 channel established!"

### Stateful TCP Tracking
**What it means:** It remembers the "state" of connections (like "connection started", "data transferring", "connection closed").

**Why it matters:** Some attacks send packets that don't make sense for the connection state.

**Example:** "Received FIN packet but connection was never established - SUSPICIOUS!"

---

## What Makes This Special?

### 1. **Comprehensive**
- Not just one tool, but a complete toolkit
- Does everything from capture to reporting

### 2. **Smart Detection**
- Not just simple rules, but intelligent pattern recognition
- Uses time windows, baselines, and correlation

### 3. **Easy to Use**
- Both command-line and GUI options
- Works with existing PCAP files (from Wireshark, etc.)

### 4. **Extensible**
- Can add custom malicious IP lists
- Can adjust thresholds for your network
- Can add new detection methods

---

## The Technical Stack (What Powers It)

**Python Libraries Used:**
- **Scapy:** The "Swiss Army knife" for network packets (captures and analyzes)
- **Pandas:** For organizing data (like Excel for Python)
- **Matplotlib/Seaborn:** For making charts and graphs
- **Tkinter:** For the GUI (makes windows and buttons)
- **Click:** For the command-line interface (makes commands easy)

**Think of it like:**
- Scapy = The camera and microscope
- Pandas = The filing cabinet
- Matplotlib = The artist
- Tkinter = The user interface designer
- Click = The command interpreter

---

## Common Questions

### Q: Do I need to be a hacker to use this?
**A:** No! The GUI makes it easy. Just click buttons and select files.

### Q: Will this slow down my network?
**A:** No. It only READS traffic (like watching), it doesn't interfere with it.

### Q: Can I use this on Windows?
**A:** Yes! But for live capture, you need Npcap installed. Or just analyze existing PCAP files.

### Q: What if I don't have network traffic to analyze?
**A:** You can use test traffic generators, or download sample PCAP files from public datasets.

### Q: Is this legal?
**A:** Only use on networks you own or have permission to monitor! Unauthorized monitoring is illegal.

---

## Summary: The Elevator Pitch

**"SpikeGuard is like a security camera + detective + reporter for your computer network. It watches everything, understands what's happening, spots bad guys, and writes reports with pretty pictures. Use it to find attacks, investigate incidents, or just understand what's happening on your network."**

---

## How to Get Started

1. **Install dependencies:** `pip install -r requirements.txt`
2. **Try the GUI:** `python gui.py`
3. **Or use command line:** `python main.py interfaces` (to see available network interfaces)
4. **Capture some traffic:** `python main.py capture -i auto -o test.pcap -c 100`
5. **Analyze it:** `python main.py analyze test.pcap`

That's it! You're now a network forensics investigator! 🕵️‍♂️

---

## Final Thoughts

SpikeGuard combines:
- **Network engineering** (understanding how networks work)
- **Security analysis** (finding threats)
- **Data science** (analyzing patterns)
- **Software engineering** (building tools)

It's a complete solution for network security analysis, from beginner-friendly GUI to advanced command-line tools. Whether you're investigating an attack, monitoring your network, or learning about network security, this toolkit has you covered!

---

*Remember: With great power comes great responsibility. Always use network monitoring tools ethically and legally!*

