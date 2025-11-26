import subprocess
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Optional


def run_adb_command(command: str, shell: bool = True) -> Optional[str]:
    try:
        full_command = f"adb {command}"
        result = subprocess.run(
            full_command,
            shell=shell,
            capture_output=True,
            timeout=60
        )
        if result.returncode == 0:
            try:
                output = result.stdout.decode('utf-8', errors='replace').strip()
                return output
            except Exception:
                try:
                    output = result.stdout.decode('latin1', errors='replace').strip()
                    return output
                except Exception:
                    return None
        else:
            return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        return None


def check_adb_connection() -> bool:
    result = run_adb_command("devices")
    if result:
        lines = result.split('\n')[1:]
        devices = [line for line in lines if line.strip() and '\tdevice' in line]
        return len(devices) > 0
    return False


def parse_date(date_str: str) -> str:
    if not date_str or date_str == "N/A":
        return "1970-01-01 00:00:00"
    try:
        if isinstance(date_str, str) and date_str.isdigit():
            timestamp_ms = int(date_str)
            if timestamp_ms > 1000000000000:
                timestamp = timestamp_ms / 1000
            else:
                timestamp = timestamp_ms
            if timestamp > 0:
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return "1970-01-01 00:00:00"
        else:
            if isinstance(date_str, str) and date_str.startswith("1970"):
                return "1970-01-01 00:00:00"
            return date_str if date_str else "1970-01-01 00:00:00"
    except (ValueError, OSError, OverflowError):
        return "1970-01-01 00:00:00"


def sanitize_package_name(package_name: str) -> str:
    if "installer=" in package_name:
        return package_name.split("installer=")[0].strip()
    return package_name.strip()
