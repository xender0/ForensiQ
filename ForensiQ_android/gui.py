
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from datetime import datetime
from pathlib import Path
import sys

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

class ForensicsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ForensiQ (Android)")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        self.extract_apps = tk.BooleanVar(value=True)
        self.extract_permissions = tk.BooleanVar(value=True)
        self.extract_device_info = tk.BooleanVar(value=True)
        self.extract_filesystem = tk.BooleanVar(value=True)
        self.extract_location = tk.BooleanVar(value=True)
        self.extract_network = tk.BooleanVar(value=True)
        self.extract_contacts = tk.BooleanVar(value=True)
        self.extract_sms = tk.BooleanVar(value=True)
        self.extract_call_logs = tk.BooleanVar(value=True)
        
        self.is_extracting = False
        self.output_file = None
        
        self.create_widgets()
        self.check_adb_on_startup()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(
            main_frame, 
            text="ForensiQ (Android)",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Checking ADB connection...",
            foreground="orange"
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.refresh_btn = ttk.Button(
            status_frame,
            text="Refresh Connection",
            command=self.check_adb_connection
        )
        self.refresh_btn.grid(row=0, column=1, padx=(10, 0))
        
        options_frame = ttk.LabelFrame(main_frame, text="Extraction Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(
            options_frame,
            text="Installed Applications",
            variable=self.extract_apps
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Application Permissions",
            variable=self.extract_permissions
        ).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Device Information",
            variable=self.extract_device_info
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Filesystem Information",
            variable=self.extract_filesystem
        ).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Location Data",
            variable=self.extract_location
        ).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Network Data",
            variable=self.extract_network
        ).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Contacts",
            variable=self.extract_contacts
        ).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="SMS Messages",
            variable=self.extract_sms
        ).grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Checkbutton(
            options_frame,
            text="Call Logs",
            variable=self.extract_call_logs
        ).grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        
        button_frame = ttk.Frame(options_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Select All",
            command=self.select_all
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame,
            text="Deselect All",
            command=self.deselect_all
        ).grid(row=0, column=1, padx=5)
        
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Save to:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.output_path_var = tk.StringVar(value="Current Directory (auto-named)")
        ttk.Label(output_frame, textvariable=self.output_path_var).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Button(
            output_frame,
            text="Browse...",
            command=self.browse_output_path
        ).grid(row=0, column=2, padx=(5, 0))
        
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        log_frame = ttk.LabelFrame(main_frame, text="Extraction Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        self.start_btn = ttk.Button(
            action_frame,
            text="Start Extraction",
            command=self.start_extraction,
            style="Accent.TButton"
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(
            action_frame,
            text="Stop",
            command=self.stop_extraction,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(
            action_frame,
            text="Clear Log",
            command=self.clear_log
        ).grid(row=0, column=2, padx=5)
        
        ttk.Button(
            action_frame,
            text="Open Output Folder",
            command=self.open_output_folder
        ).grid(row=0, column=3, padx=5)
        
        ttk.Button(
            action_frame,
            text="Open HTML Report",
            command=self.open_html_report
        ).grid(row=0, column=4, padx=5)
        
        ttk.Button(
            action_frame,
            text="Exit",
            command=self.root.quit
        ).grid(row=0, column=5, padx=5)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def check_adb_on_startup(self):
        self.check_adb_connection()
    
    def check_adb_connection(self):
        self.log_message("Checking ADB connection...")
        connected = check_adb_connection()
        
        if connected:
            self.status_label.config(
                text="✓ Device Connected",
                foreground="green"
            )
            self.log_message("✓ Device connected successfully")
            self.start_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(
                text="✗ No Device Connected",
                foreground="red"
            )
            self.log_message("✗ No Android device found. Please connect a device and enable USB debugging.")
            self.start_btn.config(state=tk.DISABLED)
    
    def select_all(self):
        self.extract_apps.set(True)
        self.extract_permissions.set(True)
        self.extract_device_info.set(True)
        self.extract_filesystem.set(True)
        self.extract_location.set(True)
        self.extract_network.set(True)
        self.extract_contacts.set(True)
        self.extract_sms.set(True)
        self.extract_call_logs.set(True)
    
    def deselect_all(self):
        self.extract_apps.set(False)
        self.extract_permissions.set(False)
        self.extract_device_info.set(False)
        self.extract_filesystem.set(False)
        self.extract_location.set(False)
        self.extract_network.set(False)
        self.extract_contacts.set(False)
        self.extract_sms.set(False)
        self.extract_call_logs.set(False)
    
    def browse_output_path(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_path_var.set(directory)
    
    def start_extraction(self):
        if not any([
            self.extract_apps.get(),
            self.extract_permissions.get(),
            self.extract_device_info.get(),
            self.extract_filesystem.get(),
            self.extract_location.get(),
            self.extract_network.get(),
            self.extract_contacts.get(),
            self.extract_sms.get(),
            self.extract_call_logs.get()
        ]):
            messagebox.showwarning(
                "No Selection",
                "Please select at least one extraction option."
            )
            return
        
        if not check_adb_connection():
            messagebox.showerror(
                "No Device",
                "No Android device connected. Please connect a device and enable USB debugging."
            )
            return
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_extracting = True
        
        self.progress_bar.start(10)
        
        thread = threading.Thread(target=self.run_extraction, daemon=True)
        thread.start()
    
    def stop_extraction(self):
        self.is_extracting = False
        self.log_message("Stopping extraction...")
        self.progress_bar.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_var.set("Stopped")
    
    def run_extraction(self):
        try:
            self.log_message("=" * 60)
            self.log_message("Starting extraction...")
            self.log_message("=" * 60)
            
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
            
            total_steps = sum([
                self.extract_apps.get(),
                self.extract_permissions.get(),
                self.extract_device_info.get(),
                self.extract_filesystem.get(),
                self.extract_location.get(),
                self.extract_network.get(),
                self.extract_contacts.get(),
                self.extract_sms.get(),
                self.extract_call_logs.get()
            ])
            
            current_step = 0
            
            if self.extract_apps.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting installed applications...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting installed applications...")
                try:
                    apps = extract_installed_apps()
                    output["installed_apps"] = apps
                    self.log_message(f"✓ Extracted {len(apps)} applications")
                except Exception as e:
                    self.log_message(f"✗ Error extracting apps: {str(e)}")
            
            if self.extract_permissions.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting application permissions...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting application permissions...")
                try:
                    permissions = extract_app_permissions()
                    output["app_permissions"] = permissions
                    self.log_message(f"✓ Extracted permissions for {len(permissions)} applications")
                except Exception as e:
                    self.log_message(f"✗ Error extracting permissions: {str(e)}")
            
            if self.extract_device_info.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting device information...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting device information...")
                try:
                    device_info = extract_device_info()
                    output["device_info"] = device_info
                    self.log_message("✓ Device information extracted")
                except Exception as e:
                    self.log_message(f"✗ Error extracting device info: {str(e)}")
            
            if self.extract_filesystem.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting filesystem information...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting filesystem information...")
                try:
                    filesystem = extract_filesystem_info()
                    output["filesystem"] = filesystem
                    self.log_message("✓ Filesystem information extracted")
                except Exception as e:
                    self.log_message(f"✗ Error extracting filesystem: {str(e)}")
            
            if self.extract_location.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting location data...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting location data...")
                try:
                    location = extract_location_data()
                    output["location"] = location
                    self.log_message("✓ Location data extracted")
                except Exception as e:
                    self.log_message(f"✗ Error extracting location: {str(e)}")
            
            if self.extract_network.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting network data...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting network data...")
                try:
                    network = extract_network_data()
                    output["network"] = network
                    self.log_message("✓ Network data extracted")
                except Exception as e:
                    self.log_message(f"✗ Error extracting network: {str(e)}")
            
            if self.extract_contacts.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting contacts...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting contacts...")
                try:
                    contacts = extract_contacts()
                    output["contacts"] = contacts
                    self.log_message(f"✓ Extracted {len(contacts)} contacts")
                except Exception as e:
                    self.log_message(f"✗ Error extracting contacts: {str(e)}")
            
            if self.extract_sms.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting SMS messages...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting SMS messages...")
                try:
                    sms = extract_sms()
                    output["sms"] = sms
                    self.log_message(f"✓ Extracted {len(sms)} SMS messages")
                except Exception as e:
                    self.log_message(f"✗ Error extracting SMS: {str(e)}")
            
            if self.extract_call_logs.get() and self.is_extracting:
                current_step += 1
                self.progress_var.set(f"[{current_step}/{total_steps}] Extracting call logs...")
                self.log_message(f"\n[{current_step}/{total_steps}] Extracting call logs...")
                try:
                    call_logs = extract_call_logs()
                    output["call_logs"] = call_logs
                    self.log_message(f"✓ Extracted {len(call_logs)} call logs")
                except Exception as e:
                    self.log_message(f"✗ Error extracting call logs: {str(e)}")
            
            if not self.is_extracting:
                self.log_message("\nExtraction cancelled by user.")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = self.output_path_var.get()
            
            if output_dir == "Current Directory (auto-named)":
                output_file = Path(f"forensics_output_{timestamp}.json")
            else:
                output_file = Path(output_dir) / f"forensics_output_{timestamp}.json"
            
            self.progress_var.set("Saving results...")
            self.log_message(f"\nSaving results to {output_file}...")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            self.output_file = str(output_file)
            self.log_message(f"✓ Results saved to {output_file}")
            
            results_txt = output_file.parent / "results.txt"
            self.log_message(f"\nSaving tabular format to {results_txt}...")
            try:
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
                
                self.log_message(f"✓ Tabular results saved to {results_txt}")
            except Exception as e:
                self.log_message(f"✗ Error saving tabular format: {str(e)}")
            
            html_file = output_file.parent / "forensics_report.html"
            self.log_message(f"\nGenerating HTML report...")
            try:
                html_path = generate_html_report(output, output_file)
                self.log_message(f"✓ HTML report saved to {html_path}")
            except Exception as e:
                self.log_message(f"✗ Error generating HTML report: {str(e)}")
            
            self.log_message("\n" + "=" * 60)
            self.log_message("EXTRACTION COMPLETE")
            self.log_message("=" * 60)
            self.log_message(f"Timestamp: {output['collection_timestamp']}")
            self.log_message(f"Installed Apps: {len(output['installed_apps'])}")
            self.log_message(f"Apps with Permissions: {len(output['app_permissions'])}")
            self.log_message(f"Contacts: {len(output['contacts'])}")
            self.log_message(f"SMS Messages: {len(output['sms'])}")
            self.log_message(f"Call Logs: {len(output['call_logs'])}")
            self.log_message(f"JSON Output: {output_file}")
            self.log_message(f"Tabular Output: {results_txt}")
            try:
                html_file = output_file.parent / "forensics_report.html"
                if html_file.exists():
                    self.log_message(f"HTML Report: {html_file}")
            except:
                pass
            self.log_message("=" * 60)
            
            self.progress_var.set("Extraction complete!")
            
            html_file = output_file.parent / "forensics_report.html"
            html_msg = f"\nHTML Report: {html_file}" if html_file.exists() else ""
            self.root.after(0, lambda: messagebox.showinfo(
                "Extraction Complete",
                f"Extraction completed successfully!\n\nOutput saved to:\n{output_file}{html_msg}"
            ))
            
        except Exception as e:
            error_msg = f"Error during extraction: {str(e)}"
            self.log_message(f"\n✗ {error_msg}")
            self.progress_var.set("Error occurred!")
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.progress_bar.stop()
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.is_extracting = False
    
    def open_output_folder(self):
        if self.output_file:
            import os
            import platform
            folder = os.path.dirname(os.path.abspath(self.output_file))
            
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":
                os.system(f"open '{folder}'")
            else:
                os.system(f"xdg-open '{folder}'")
        else:
            messagebox.showinfo("No Output", "No output file has been created yet.")
    
    def open_html_report(self):
        if self.output_file:
            import os
            import platform
            html_file = Path(self.output_file).parent / "forensics_report.html"
            
            if html_file.exists():
                html_path = str(html_file.absolute())
                if platform.system() == "Windows":
                    os.startfile(html_path)
                elif platform.system() == "Darwin":
                    os.system(f"open '{html_path}'")
                else:
                    os.system(f"xdg-open '{html_path}'")
            else:
                messagebox.showinfo("No Report", "HTML report not found. Please run extraction first.")
        else:
            messagebox.showinfo("No Output", "No output file has been created yet.")

def main():
    root = tk.Tk()
    app = ForensicsGUI(root)
    root.mainloop()

#this is harmless code

if __name__ == "__main__":
    main()

