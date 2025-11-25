"""
Alert system for ForensiQ
Monitors reports for suspicious findings and generates alerts
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config_manager import ConfigManager

class AlertSystem:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.alerts_file = "alerts.json"
        self.alerts = self.load_alerts()
    
    def load_alerts(self) -> List[Dict[str, Any]]:
        """Load alerts from file."""
        if os.path.exists(self.alerts_file):
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_alerts(self):
        """Save alerts to file."""
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving alerts: {e}")
    
    def check_report(self, report_path: str, report_name: str) -> List[Dict[str, Any]]:
        """Check a report for suspicious findings."""
        if not self.config.get_setting("enable_alerts", True):
            return []
        
        new_alerts = []
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for suspicious patterns
            if "Administrators" in report_name:
                alerts = self._check_administrators(content, report_name)
                new_alerts.extend(alerts)
            
            if "Firewall" in report_name:
                alerts = self._check_firewall(content, report_name)
                new_alerts.extend(alerts)
            
            if "Process" in report_name or "Service" in report_name:
                alerts = self._check_processes(content, report_name)
                new_alerts.extend(alerts)
            
            if "Network" in report_name or "TCP" in report_name:
                alerts = self._check_network(content, report_name)
                new_alerts.extend(alerts)
            
            # Save new alerts
            for alert in new_alerts:
                self.alerts.append(alert)
            
            if new_alerts:
                self.save_alerts()
            
            return new_alerts
        except Exception as e:
            print(f"Error checking report: {e}")
            return []
    
    def _check_administrators(self, content: str, report_name: str) -> List[Dict[str, Any]]:
        """Check administrators report for suspicious users."""
        alerts = []
        if not self.config.config.get("alerts", {}).get("new_administrators", True):
            return alerts
        
        # Simple check - in production, compare with baseline
        if "Administrator" in content or "admin" in content.lower():
            alerts.append({
                "type": "security",
                "severity": "high",
                "title": "Administrator Account Detected",
                "message": f"Administrator accounts found in {report_name}",
                "report": report_name,
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False
            })
        
        return alerts
    
    def _check_firewall(self, content: str, report_name: str) -> List[Dict[str, Any]]:
        """Check firewall report for suspicious rules."""
        alerts = []
        if not self.config.config.get("alerts", {}).get("firewall_changes", True):
            return alerts
        
        # Check for disabled firewall or suspicious rules
        if "Disabled" in content or "Allow" in content:
            alerts.append({
                "type": "security",
                "severity": "medium",
                "title": "Firewall Configuration Alert",
                "message": f"Firewall rules detected in {report_name}",
                "report": report_name,
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False
            })
        
        return alerts
    
    def _check_processes(self, content: str, report_name: str) -> List[Dict[str, Any]]:
        """Check processes/services for suspicious activity."""
        alerts = []
        if not self.config.config.get("alerts", {}).get("suspicious_processes", True):
            return alerts
        
        suspicious_keywords = ["powershell", "cmd", "wscript", "cscript", "regsvr32"]
        content_lower = content.lower()
        
        for keyword in suspicious_keywords:
            if keyword in content_lower:
                alerts.append({
                    "type": "security",
                    "severity": "medium",
                    "title": f"Suspicious Process: {keyword}",
                    "message": f"Potentially suspicious process detected in {report_name}",
                    "report": report_name,
                    "timestamp": datetime.now().isoformat(),
                    "acknowledged": False
                })
                break
        
        return alerts
    
    def _check_network(self, content: str, report_name: str) -> List[Dict[str, Any]]:
        """Check network connections for anomalies."""
        alerts = []
        if not self.config.config.get("alerts", {}).get("network_anomalies", True):
            return alerts
        
        # Check for unusual ports or connections
        if "LISTENING" in content or "ESTABLISHED" in content:
            alerts.append({
                "type": "network",
                "severity": "low",
                "title": "Network Activity Detected",
                "message": f"Active network connections found in {report_name}",
                "report": report_name,
                "timestamp": datetime.now().isoformat(),
                "acknowledged": False
            })
        
        return alerts
    
    def get_unacknowledged_alerts(self) -> List[Dict[str, Any]]:
        """Get all unacknowledged alerts."""
        return [a for a in self.alerts if not a.get("acknowledged", False)]
    
    def acknowledge_alert(self, alert_index: int):
        """Mark an alert as acknowledged."""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index]["acknowledged"] = True
            self.save_alerts()
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get alerts by severity level."""
        return [a for a in self.alerts if a.get("severity") == severity]

