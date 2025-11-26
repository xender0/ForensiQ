import re
from typing import Optional
from datetime import datetime


def format_bytes(bytes_value: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def validate_ip(ip_address: str) -> bool:
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_address):
        return False
    
    parts = ip_address.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def validate_port(port: int) -> bool:
    return 1 <= port <= 65535


def get_protocol_name(proto_num: int) -> str:
    protocols = {
        1: 'ICMP',
        6: 'TCP',
        17: 'UDP',
        41: 'IPv6',
        47: 'GRE',
        50: 'ESP',
        51: 'AH'
    }
    return protocols.get(proto_num, f'Protocol-{proto_num}')


def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    
    import math
    entropy = 0
    for x in range(256):
        p_x = float(data.count(bytes([x]))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    
    return entropy

