from typing import List, Dict
from ..utils import run_adb_command


def extract_app_permissions() -> Dict[str, List[str]]:
    permissions_map = {}
    packages_output = run_adb_command("shell pm list packages")
    if not packages_output:
        return permissions_map
    packages = []
    for line in packages_output.split('\n'):
        if line.startswith('package:'):
            package_name = line.replace('package:', '').strip()
            packages.append(package_name)
    for package_name in packages:
        try:
            granted_output = run_adb_command(f"shell dumpsys package {package_name} | grep -A 100 'granted=true'")
            permissions_output = run_adb_command(f"shell dumpsys package {package_name} | grep -E 'permission|requested'")
            permissions = []
            if granted_output:
                for line in granted_output.split('\n'):
                    if 'granted=true' in line or 'android.permission' in line:
                        perm_match = line.strip().split()[0] if line.strip() else ''
                        if 'android.permission' in perm_match or 'com.' in perm_match:
                            perm = perm_match.split('[')[0].split('(')[0].strip()
                            if perm and perm not in permissions:
                                permissions.append(perm)
            pm_perms = run_adb_command(f"shell pm list permissions -g -d -u | grep -B 1 -A 1 {package_name}")
            direct_perms = run_adb_command(f"shell dumpsys package {package_name} | grep -E '^\\s+android\\.permission|^\\s+com\\..*\\.permission'")
            if direct_perms:
                for line in direct_perms.split('\n'):
                    perm = line.strip()
                    if perm and perm not in permissions:
                        permissions.append(perm)
            if permissions:
                permissions_map[package_name] = sorted(list(set(permissions)))
            else:
                permissions_map[package_name] = []
        except Exception as e:
            print(f"Error extracting permissions for {package_name}: {str(e)}")
            permissions_map[package_name] = []
    return permissions_map
