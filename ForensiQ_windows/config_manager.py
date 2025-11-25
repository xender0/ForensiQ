"""
Configuration management for ForensiQ
Handles settings, preferences, and scan profiles
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

CONFIG_FILE = "forensiq_config.json"
DEFAULT_CONFIG = {
    "version": "1.0",
    "settings": {
        "theme": "dark",
        "auto_generate_manifest": True,
        "default_export_format": "html",
        "enable_alerts": True,
        "alert_threshold": "medium",
        "archive_reports": True,
        "archive_retention_days": 30
    },
    "scan_profiles": {},
    "alerts": {
        "new_administrators": True,
        "firewall_changes": True,
        "suspicious_processes": True,
        "network_anomalies": True
    },
    "api_keys": {
        "virustotal": "",
        "haveibeenpwned": ""
    },
    "last_scan": None,
    "report_history": []
}

class ConfigManager:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(config)
                    return merged
            except Exception as e:
                print(f"Error loading config: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.config.get("settings", {}).get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value."""
        if "settings" not in self.config:
            self.config["settings"] = {}
        self.config["settings"][key] = value
        self.save_config()
    
    def get_scan_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a scan profile by name."""
        return self.config.get("scan_profiles", {}).get(name)
    
    def save_scan_profile(self, name: str, scripts: list, description: str = ""):
        """Save a scan profile."""
        if "scan_profiles" not in self.config:
            self.config["scan_profiles"] = {}
        
        self.config["scan_profiles"][name] = {
            "scripts": scripts,
            "description": description,
            "created": datetime.now().isoformat(),
            "last_used": None
        }
        self.save_config()
    
    def add_report_to_history(self, report_name: str, report_path: str):
        """Add a report to history."""
        if "report_history" not in self.config:
            self.config["report_history"] = []
        
        entry = {
            "name": report_name,
            "path": report_path,
            "timestamp": datetime.now().isoformat()
        }
        self.config["report_history"].insert(0, entry)
        
        # Keep only last 100 entries
        if len(self.config["report_history"]) > 100:
            self.config["report_history"] = self.config["report_history"][:100]
        
        self.save_config()
    
    def get_api_key(self, service: str) -> str:
        """Get API key for a service."""
        return self.config.get("api_keys", {}).get(service, "")
    
    def set_api_key(self, service: str, key: str):
        """Set API key for a service."""
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        self.config["api_keys"][service] = key
        self.save_config()

