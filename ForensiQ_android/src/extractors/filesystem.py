from typing import Dict, List
from ..utils import run_adb_command


def extract_filesystem_info() -> Dict:
    filesystem_info = {}
    mount_output = run_adb_command("shell mount")
    filesystem_info['mount_points'] = mount_output.split('\n') if mount_output else []
    df_output = run_adb_command("shell df -h")
    filesystem_info['disk_usage'] = df_output.split('\n') if df_output else []
    filesystem_info['filesystem_type'] = run_adb_command("shell mount | grep ' / '") or "N/A"
    root_dirs = run_adb_command("shell ls -la /")
    filesystem_info['root_directory'] = root_dirs.split('\n') if root_dirs else []
    data_dirs = run_adb_command("shell ls -la /data")
    filesystem_info['data_directory'] = data_dirs.split('\n') if data_dirs else []
    system_dirs = run_adb_command("shell ls -la /system")
    filesystem_info['system_directory'] = system_dirs.split('\n') if system_dirs else []
    external_storage = run_adb_command("shell ls -la /sdcard")
    filesystem_info['external_storage'] = external_storage.split('\n') if external_storage else []
    partitions = run_adb_command("shell cat /proc/partitions")
    filesystem_info['partitions'] = partitions.split('\n') if partitions else []
    block_devices = run_adb_command("shell ls -la /dev/block")
    filesystem_info['block_devices'] = block_devices.split('\n') if block_devices else []
    return filesystem_info


def extract_directory_tree(path: str, max_depth: int = 3) -> List[str]:
    tree = []
    try:
        find_output = run_adb_command(f"shell find {path} -maxdepth {max_depth} -type d 2>/dev/null")
        if find_output:
            tree = find_output.split('\n')
    except Exception as e:
        print(f"Error extracting directory tree from {path}: {str(e)}")
    return tree
