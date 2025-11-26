from typing import Dict
from ..utils import run_adb_command


def extract_device_info() -> Dict:
    device_info = {}
    device_info['model'] = run_adb_command("shell getprop ro.product.model") or "N/A"
    device_info['manufacturer'] = run_adb_command("shell getprop ro.product.manufacturer") or "N/A"
    device_info['brand'] = run_adb_command("shell getprop ro.product.brand") or "N/A"
    device_info['device'] = run_adb_command("shell getprop ro.product.device") or "N/A"
    device_info['android_version'] = run_adb_command("shell getprop ro.build.version.release") or "N/A"
    device_info['sdk_version'] = run_adb_command("shell getprop ro.build.version.sdk") or "N/A"
    device_info['build_id'] = run_adb_command("shell getprop ro.build.id") or "N/A"
    device_info['build_type'] = run_adb_command("shell getprop ro.build.type") or "N/A"
    device_info['hardware'] = run_adb_command("shell getprop ro.hardware") or "N/A"
    device_info['cpu_abi'] = run_adb_command("shell getprop ro.product.cpu.abi") or "N/A"
    device_info['cpu_abi2'] = run_adb_command("shell getprop ro.product.cpu.abi2") or "N/A"
    device_info['display_density'] = run_adb_command("shell getprop ro.sf.lcd_density") or "N/A"
    device_info['wifi_mac'] = run_adb_command("shell cat /sys/class/net/wlan0/address") or "N/A"
    device_info['serial'] = run_adb_command("get-serialno") or "N/A"
    device_info['android_id'] = run_adb_command("shell settings get secure android_id") or "N/A"
    storage_output = run_adb_command("shell df -h /data")
    device_info['storage_info'] = storage_output or "N/A"
    memory_output = run_adb_command("shell cat /proc/meminfo | head -5")
    device_info['memory_info'] = memory_output or "N/A"
    battery_output = run_adb_command("shell dumpsys battery")
    device_info['battery_info'] = battery_output or "N/A"
    screen_output = run_adb_command("shell dumpsys window displays")
    device_info['screen_info'] = screen_output or "N/A"
    packages_count = run_adb_command("shell pm list packages | wc -l")
    device_info['installed_apps_count'] = packages_count.strip() if packages_count else "N/A"
    boot_time = run_adb_command("shell uptime -s")
    device_info['boot_time'] = boot_time or "N/A"
    device_info['security_patch'] = run_adb_command("shell getprop ro.build.version.security_patch") or "N/A"
    kernel_version = run_adb_command("shell cat /proc/version")
    device_info['kernel_version'] = kernel_version or "N/A"
    return device_info
