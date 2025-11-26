from typing import Dict, List
from ..utils import run_adb_command
import json


def extract_network_data() -> Dict:
    network_data = {}
    interfaces = run_adb_command("shell ip addr show")
    network_data['network_interfaces'] = interfaces.split('\n') if interfaces else []
    ip_info = run_adb_command("shell ip addr")
    network_data['ip_addresses'] = ip_info.split('\n') if ip_info else []
    wifi_info = run_adb_command("shell dumpsys wifi")
    network_data['wifi_info'] = wifi_info or "N/A"
    wifi_ssid = run_adb_command("shell dumpsys wifi | grep -i 'current SSID'")
    network_data['connected_wifi_ssid'] = wifi_ssid or "N/A"
    saved_wifi = run_adb_command("shell dumpsys wifi | grep -E 'SSID|BSSID|networkId'")
    network_data['saved_wifi_networks'] = saved_wifi.split('\n') if saved_wifi else []
    network_config = run_adb_command("shell cat /proc/net/route")
    network_data['network_routes'] = network_config.split('\n') if network_config else []
    dns_info = run_adb_command("shell getprop | grep -i dns")
    network_data['dns_servers'] = dns_info.split('\n') if dns_info else []
    netstat = run_adb_command("shell netstat -tun")
    network_data['active_connections'] = netstat.split('\n') if netstat else []
    network_stats = run_adb_command("shell cat /proc/net/dev")
    network_data['network_statistics'] = network_stats.split('\n') if network_stats else []
    telephony_info = run_adb_command("shell dumpsys telephony.registry")
    network_data['telephony_info'] = telephony_info or "N/A"
    carrier = run_adb_command("shell getprop gsm.operator.alpha")
    network_data['carrier'] = carrier or "N/A"
    phone_number = run_adb_command("shell service call iphonesubinfo 1")
    network_data['phone_number_info'] = phone_number or "N/A"
    imei = run_adb_command("shell service call iphonesubinfo 1 | grep -oE '[0-9]{15}'")
    network_data['imei'] = imei or "N/A"
    bluetooth_info = run_adb_command("shell dumpsys bluetooth_manager")
    network_data['bluetooth_info'] = bluetooth_info or "N/A"
    bt_devices = run_adb_command("shell dumpsys bluetooth_manager | grep -i 'device\\|name'")
    network_data['bluetooth_devices'] = bt_devices.split('\n') if bt_devices else []
    vpn_info = run_adb_command("shell dumpsys vpn")
    network_data['vpn_info'] = vpn_info or "N/A"
    network_security = run_adb_command("shell dumpsys connectivity")
    network_data['connectivity_info'] = network_security or "N/A"
    proxy_host = run_adb_command("shell settings get global http_proxy")
    network_data['proxy_settings'] = proxy_host or "N/A"
    data_usage = run_adb_command("shell dumpsys netstats")
    network_data['data_usage'] = data_usage or "N/A"
    return network_data


def extract_network_logs() -> List[str]:
    logs = []
    logcat_output = run_adb_command("shell logcat -d | grep -iE 'network|wifi|bluetooth|connectivity' | tail -100")
    if logcat_output:
        logs = logcat_output.split('\n')
    return logs
