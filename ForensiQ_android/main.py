#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from pathlib import Path

from src.utils import check_adb_connection
from src.extractors import (
    extract_installed_apps,
    extract_app_permissions,
    extract_device_info,
    extract_filesystem_info,
    extract_location_data,
    extract_network_data,
    extract_contacts,
    extract_contacts_table,
    extract_sms,
    extract_sms_table,
    extract_call_logs,
    extract_call_logs_table
)
from src.html_report import generate_html_report


def main():
    print("=" * 60)
    print("ForensiQ (Android)")
    print("=" * 60)
    
    print("\n[1/7] Checking ADB connection...")
    if not check_adb_connection():
        print("ERROR: No Android device connected via ADB")
        print("Please ensure:")
        print("  1. ADB is installed and in your PATH")
        print("  2. USB debugging is enabled on the device")
        print("  3. Device is connected and authorized")
        sys.exit(1)
    print("✓ Device connected")
    
    output = {
        "collection_timestamp": datetime.now().isoformat(),
        "installed_apps": [],
        "app_permissions": {},
        "device_info": {},
        "filesystem": {},
        "location": {},
        "network": {},
        "contacts": [],
        "sms": [],
        "call_logs": []
    }
    
    try:
        print("\n[2/7] Extracting installed applications...")
        apps = extract_installed_apps()
        output["installed_apps"] = apps
        print(f"✓ Extracted {len(apps)} applications")
        
        print("\n[3/7] Extracting application permissions...")
        permissions = extract_app_permissions()
        output["app_permissions"] = permissions
        print(f"✓ Extracted permissions for {len(permissions)} applications")
        
        print("\n[4/7] Extracting device information...")
        device_info = extract_device_info()
        output["device_info"] = device_info
        print("✓ Device information extracted")
        
        print("\n[5/7] Extracting filesystem information...")
        filesystem = extract_filesystem_info()
        output["filesystem"] = filesystem
        print("✓ Filesystem information extracted")
        
        print("\n[6/7] Extracting location data...")
        location = extract_location_data()
        output["location"] = location
        print("✓ Location data extracted")
        
        print("\n[7/10] Extracting network data...")
        network = extract_network_data()
        output["network"] = network
        print("✓ Network data extracted")
        
        print("\n[8/10] Extracting contacts...")
        contacts = extract_contacts()
        output["contacts"] = contacts
        print(f"✓ Extracted {len(contacts)} contacts")
        
        print("\n[9/10] Extracting SMS messages...")
        sms = extract_sms()
        output["sms"] = sms
        print(f"✓ Extracted {len(sms)} SMS messages")
        
        print("\n[10/10] Extracting call logs...")
        call_logs = extract_call_logs()
        output["call_logs"] = call_logs
        print(f"✓ Extracted {len(call_logs)} call logs")
        
    except KeyboardInterrupt:
        print("\n\nExtraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(f"forensics_output_{timestamp}.json")
    
    print(f"\n[INFO] Saving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Results saved to {output_file}")
    
    results_txt = Path("results.txt")
    print(f"\n[INFO] Saving tabular format to {results_txt}...")
    with open(results_txt, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("FORENSIQ (ANDROID) EXTRACTION RESULTS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Collection Timestamp: {output['collection_timestamp']}\n\n")
        
        if output.get("contacts"):
            f.write("\n" + "=" * 80 + "\n")
            f.write("CONTACTS\n")
            f.write("=" * 80 + "\n")
            f.write(extract_contacts_table())
        
        if output.get("sms"):
            f.write("\n" + "=" * 80 + "\n")
            f.write("SMS MESSAGES\n")
            f.write("=" * 80 + "\n")
            f.write(extract_sms_table())
        
        if output.get("call_logs"):
            f.write("\n" + "=" * 80 + "\n")
            f.write("CALL LOGS\n")
            f.write("=" * 80 + "\n")
            f.write(extract_call_logs_table())
    
    print(f"✓ Tabular results saved to {results_txt}")
    
    print(f"\n[INFO] Generating HTML report...")
    try:
        html_file = generate_html_report(output, output_file)
        print(f"✓ HTML report saved to {html_file}")
    except Exception as e:
        print(f"✗ Error generating HTML report: {str(e)}")
        import traceback
        traceback.print_exc()
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Timestamp: {output['collection_timestamp']}")
    print(f"Installed Apps: {len(output['installed_apps'])}")
    print(f"Apps with Permissions: {len(output['app_permissions'])}")
    print(f"Contacts: {len(output['contacts'])}")
    print(f"SMS Messages: {len(output['sms'])}")
    print(f"Call Logs: {len(output['call_logs'])}")
    print(f"JSON Output: {output_file}")
    print(f"Tabular Output: {results_txt}")
    try:
        html_file = Path("forensics_report.html")
        if html_file.exists():
            print(f"HTML Report: {html_file}")
    except:
        pass
    print("=" * 60)


if __name__ == "__main__":
    main()

