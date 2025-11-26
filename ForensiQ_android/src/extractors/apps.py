import re
from typing import List, Dict
from datetime import datetime
from ..utils import run_adb_command, parse_date, sanitize_package_name


def extract_installed_apps() -> List[Dict]:
    apps = []
    packages_output = run_adb_command("shell pm list packages -f")
    if not packages_output:
        return apps
    packages = {}
    for line in packages_output.split('\n'):
        if line.startswith('package:'):
            parts = line.replace('package:', '').split('=')
            if len(parts) == 2:
                apk_path, package_name = parts
                packages[package_name] = {'apk_path': apk_path}
    for package_name, app_info in packages.items():
        try:
            dump_output = run_adb_command(f"shell dumpsys package {package_name}")
            app_data = {
                'package_name': sanitize_package_name(package_name),
                'apk_path': app_info.get('apk_path', 'N/A'),
                'label': package_name,
                'version': 'N/A',
                'install_date': '1970-01-01 00:00:00',
                'update_date': '1970-01-01 00:00:00',
                'uid': 'N/A',
                'data_dir': f'/data/data/{package_name}'
            }
            if dump_output:
                version_match = re.search(r'versionName=([^\s]+)', dump_output)
                if version_match:
                    app_data['version'] = version_match.group(1)
            if dump_output:
                label_patterns = [
                    r'applicationLabel=\'([^\']+)\'',
                    r'applicationLabel="([^"]+)"',
                    r'applicationLabel=([^\s\n]+)',
                ]
                for pattern in label_patterns:
                    label_match = re.search(pattern, dump_output)
                    if label_match:
                        label = label_match.group(1).strip()
                        if label and label != package_name and len(label) < 100:
                            app_data['label'] = label
                            break
                if app_data['label'] == package_name:
                    pm_dump = run_adb_command(f"shell pm dump {package_name}")
                    if pm_dump:
                        label_match = re.search(r'Application Label: ([^\n]+)', pm_dump)
                        if label_match:
                            label = label_match.group(1).strip()
                            if label:
                                app_data['label'] = label
            if dump_output:
                install_match = re.search(r'firstInstallTime=(\d+)', dump_output)
                if install_match:
                    timestamp = install_match.group(1)
                    if timestamp and int(timestamp) > 0:
                        app_data['install_date'] = parse_date(timestamp)
                if app_data['install_date'] == '1970-01-01 00:00:00':
                    install_match = re.search(r'installTime=(\d+)', dump_output)
                    if install_match:
                        timestamp = install_match.group(1)
                        if timestamp and int(timestamp) > 0:
                            app_data['install_date'] = parse_date(timestamp)
                update_match = re.search(r'lastUpdateTime=(\d+)', dump_output)
                if update_match:
                    timestamp = update_match.group(1)
                    if timestamp and int(timestamp) > 0:
                        app_data['update_date'] = parse_date(timestamp)
                if app_data['update_date'] == '1970-01-01 00:00:00':
                    update_match = re.search(r'updateTime=(\d+)', dump_output)
                    if update_match:
                        timestamp = update_match.group(1)
                        if timestamp and int(timestamp) > 0:
                            app_data['update_date'] = parse_date(timestamp)
            if dump_output:
                uid_match = re.search(r'userId=(\d+)', dump_output)
                if uid_match:
                    app_data['uid'] = uid_match.group(1)
            data_dir_output = run_adb_command(f"shell pm path {package_name} | head -1")
            if data_dir_output and 'data' in data_dir_output:
                app_data['data_dir'] = f'/data/data/{package_name}'
            apps.append(app_data)
        except Exception as e:
            print(f"Error processing package {package_name}: {str(e)}")
            apps.append({
                'package_name': sanitize_package_name(package_name),
                'apk_path': app_info.get('apk_path', 'N/A'),
                'label': package_name,
                'version': 'N/A',
                'install_date': '1970-01-01 00:00:00',
                'update_date': '1970-01-01 00:00:00',
                'uid': 'N/A',
                'data_dir': f'/data/data/{package_name}'
            })
    return apps
