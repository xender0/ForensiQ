# ForensiQ

Digital forensics toolkit. Three parts and a launcher.

## ForensiQ_windows

Live response on Windows. 30 PowerShell scripts pulling artefacts - users,
admin accounts, installed software, scheduled tasks, startup entries, USB
history, saved wifi profiles, DNS cache, firewall rules, TCP connections,
Defender status - and a Python frontend that runs them and builds a HTML report.

Also has a VirusTotal scanner (file hashes and URLs), a breached email checker
that pulls saved accounts out of browsers, and alerting for things like new
admin accounts.

`python run.py` or `start.bat`. Needs an admin shell for most of it.

## ForensiQ_network

Packet capture and analysis with scapy. Live capture or an existing pcap, then
flow analysis, protocol breakdown, basic IDS rules and a report with charts.

`python run_gui.py` for the GUI, `python main.py` for CLI. Examples in
`code/examples`.

## ForensiQ_android

Android extraction over ADB. Device info, contacts, call logs, SMS, apps,
permissions, location, network config, filesystem listing. Outputs HTML.

Needs adb on PATH and USB debugging on. `python gui.py`.

## main

Launcher, three buttons. `python main_launcher.py`.

## Setup

```
pip install -r ForensiQ_windows/requirements.txt
pip install -r ForensiQ_network/code/requirements.txt
```

Android needs nothing, it's all standard library.

VirusTotal and the breach lookups need your own API keys. They go in
forensiq_config.json, which is gitignored.

To build the network exe: `cd ForensiQ_network/code` then `build.bat`.
