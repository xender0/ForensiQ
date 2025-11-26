from typing import Dict, List
from ..utils import run_adb_command
import json
import re


def extract_location_data() -> Dict:
    location_data = {}
    gps_status = run_adb_command("shell dumpsys location")
    location_data['gps_status'] = gps_status or "N/A"
    location_enabled = run_adb_command("shell settings get secure location_providers_allowed")
    location_data['location_services_enabled'] = location_enabled or "N/A"
    location_mode = run_adb_command("shell settings get secure location_mode")
    location_data['location_mode'] = location_mode or "N/A"
    last_location = run_adb_command("shell dumpsys location | grep -A 20 'Last Location'")
    location_data['last_known_location'] = last_location or "N/A"
    providers = run_adb_command("shell dumpsys location | grep -E 'Provider|LocationProvider'")
    location_data['location_providers'] = providers.split('\n') if providers else []
    network_location = run_adb_command("shell dumpsys location | grep -i 'network'")
    location_data['network_location_info'] = network_location or "N/A"
    gps_satellites = run_adb_command("shell dumpsys location | grep -i 'satellite'")
    location_data['gps_satellites'] = gps_satellites or "N/A"
    location_perms = []
    packages_output = run_adb_command("shell pm list packages")
    if packages_output:
        for line in packages_output.split('\n'):
            if line.startswith('package:'):
                package_name = line.replace('package:', '').strip()
                perm_output = run_adb_command(f"shell dumpsys package {package_name} | grep -E 'ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION'")
                if perm_output:
                    location_perms.append(package_name)
    location_data['apps_with_location_permissions'] = location_perms
    location_history = run_adb_command("shell dumpsys location | grep -A 50 'Location History'")
    location_data['location_history'] = location_history or "N/A"
    cell_info = run_adb_command("shell dumpsys telephony.registry | grep -i cell")
    location_data['cell_tower_info'] = cell_info or "N/A"
    wifi_aps = run_adb_command("shell dumpsys wifi | grep -i 'SSID\\|BSSID'")
    location_data['wifi_access_points'] = wifi_aps or "N/A"
    return location_data


def extract_location_database() -> Dict:
    location_db = {}
    db_paths = [
        "/data/data/com.google.android.gms/databases/",
        "/data/data/com.android.providers.location/",
        "/data/data/com.google.android.location/",
    ]
    for db_path in db_paths:
        db_files = run_adb_command(f"shell find {db_path} -name '*.db' 2>/dev/null")
        if db_files:
            location_db[db_path] = db_files.split('\n')
    return location_db
