import os
import subprocess
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Listbox, Scrollbar, MULTIPLE, StringVar, Frame, messagebox, Canvas, BooleanVar, Checkbutton, Tk
import sys
import webbrowser
import http.server
import socketserver
import threading
import time

# Import new modules
try:
    from config_manager import ConfigManager
    from alert_system import AlertSystem
    from report_archiver import ReportArchiver
    from export_utils import export_all_reports_to_zip, export_to_csv, export_to_json
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MODULES_AVAILABLE = False
    ConfigManager = None
    AlertSystem = None
    ReportArchiver = None

# --- List of PowerShell Data Collection Scripts ---
# Ensure these filenames match exactly what's in your project root
ps_scripts = [
    "Administrators.ps1",
    "Camera Device Info.ps1",
    "Computer System Info.ps1",
    "Connected Devices Info.ps1",
    "Disk Information Retrieval.ps1",
    "DNS Cache.ps1",
    "Executable Files Info From Obscure Places.ps1",
    "Firewall Rules.ps1",
    "Installed Programs List (From Registry).ps1",
    "Installed Software Info.ps1", # Consider removing or warning about Win32_Product
    "IP Address.ps1",
    "IP Configurations.ps1",
    "Local Group.ps1",
    "Net Adapter.ps1", # This is Get-NetAdapter based
    "Net Connection Profile.ps1",
    "Net Neighbor.ps1",
    "Net TCP Connection.ps1",
    "Network Adapter.ps1", # This is Win32_NetworkAdapter based
    "OS Info.ps1",
    "Scheduled Tasks.ps1",
    "Service Details.ps1",
    "Startup Programs.ps1",
    "USB Device Names (ever connected).ps1",
    "USB Devices.ps1",
    "User Details.ps1",
    "User Processes.ps1",
    "Wi-fi Names and Passwords.ps1",
    "Windows Defender Status.ps1",
    "wpa_check.ps1", # Added WPA Check script
]

# --- Helper Functions for PowerShell Collectors ---
def run_script(script_filename):
    """Runs a single PowerShell script."""
    try:
        status_var.set(f"Running: {script_filename}...")
        root.update_idletasks()
        # Ensure the script path is correct (assuming it's in the same dir as run.py)
        script_full_path = os.path.join(os.path.dirname(__file__), script_filename)
        if not os.path.exists(script_full_path):
            status_var.set(f"Error: {script_filename} not found at {script_full_path}")
            return False

        process = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_full_path],
            check=False, # Don't raise exception on non-zero exit, handle it
            capture_output=True,
            text=True,
        )
        if process.returncode == 0:
            status_var.set(f"Completed: {script_filename}")
            return True
        else:
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            status_var.set(f"Failed: {script_filename}. Error: {error_msg[:150]}...")
            print(f"Error running {script_filename}:\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}")
            return False
    except FileNotFoundError:
        status_var.set(f"Error: PowerShell not found. Is it in your PATH?")
        return False
    except Exception as e:
        status_var.set(f"Error running {script_filename}: {e}")
        print(f"Exception running {script_filename}: {e}")
        return False

def run_selected_collectors():
    """Runs selected PowerShell scripts from the checkboxes."""
    selected_scripts_to_run = [ps_scripts[i] for i, var in enumerate(checkbox_vars) if var.get()]

    if not selected_scripts_to_run:
        status_var.set("⚠️ No PowerShell collectors selected!")
        messagebox.showwarning("No Selection", "Please select at least one collector to run.")
        return

    progress_bar["maximum"] = len(selected_scripts_to_run)
    progress_bar["value"] = 0
    all_successful = True
    for i, script_name in enumerate(selected_scripts_to_run):
        if not run_script(script_name):
            all_successful = False
        progress_bar["value"] = i + 1
        root.update_idletasks()

    if all_successful:
        status_var.set(f"✅ Successfully executed {len(selected_scripts_to_run)} collector(s).")
    else:
        status_var.set(f"⚠️ Some PowerShell collectors failed. Check console for details.")
    generate_manifest()

def run_all_collectors():
    """Runs all PowerShell scripts in the ps_scripts list."""
    progress_bar["maximum"] = len(ps_scripts)
    progress_bar["value"] = 0
    all_successful = True
    for i, script_name in enumerate(ps_scripts):
        if not run_script(script_name):
            all_successful = False
            # Optionally, ask user if they want to continue
            # if not messagebox.askyesno("Script Failed", f"{script_name} failed. Continue?"):
            #     break
        progress_bar["value"] = i + 1
        root.update_idletasks()

    if all_successful:
        status_var.set("All PowerShell collectors executed.")
    else:
        status_var.set("Some PowerShell collectors failed. Check console for details.")
    generate_manifest()

def generate_manifest():
    """Generates a manifest.json file listing HTML reports in the output directory."""
    output_dir_name = "output"
    # Get the directory where run.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir_path = os.path.join(base_dir, output_dir_name)
    manifest_path = os.path.join(output_dir_path, "manifest.json")

    try:
        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)

        html_files = [
            f
            for f in os.listdir(output_dir_path)
            if f.endswith(".html") and f != "index.html" # Exclude the viewer itself
        ]
        html_files.sort()

        report_data = [
            {
                "name": os.path.splitext(f)[0].replace("_", " ").replace("-", " "),
                "path": f"{output_dir_name}/{f}", # Relative path for index.html
            }
            for f in html_files
        ]

        with open(manifest_path, "w") as f:
            json.dump(report_data, f, indent=4)
        print(f"Manifest generated/updated at {manifest_path}")
        
        # Check for alerts if alert system is available
        if MODULES_AVAILABLE and ConfigManager:
            try:
                config = ConfigManager()
                alert_system = AlertSystem(config)
                for report in report_data:
                    report_path = os.path.join(output_dir_path, os.path.basename(report["path"]))
                    if os.path.exists(report_path):
                        alerts = alert_system.check_report(report_path, report["name"])
                        if alerts:
                            print(f"⚠️ Alerts generated for {report['name']}: {len(alerts)}")
            except Exception as e:
                print(f"Error checking alerts: {e}")
        
    except Exception as e:
        print(f"Error generating manifest: {e}")
        status_var.set(f"Error generating manifest: {e}")


# --- Functions to Launch Other Tools ---
def launch_tool(script_path_relative, use_powershell=False, needs_admin=False, is_python_gui=False):
    """
    Generic function to launch scripts/tools.
    script_path_relative is relative to the location of this run.py script.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_full_path = os.path.join(base_dir, script_path_relative)

    if not os.path.exists(script_full_path):
        status_var.set(f"Error: Tool not found at {script_full_path}")
        print(f"Error: Tool not found at {script_full_path}")
        return

    status_text = f"Launching: {os.path.basename(script_full_path)}"
    if needs_admin:
        status_text += " (May require Admin Privileges!)"
    status_var.set(status_text)
    root.update_idletasks()

    try:
        if use_powershell:
            # For PowerShell, run and wait.
            # Admin elevation for these scripts needs run.py to be run as admin.
            print(f"Running PowerShell script: {script_full_path}")
            process = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_full_path],
                check=False, # Handle non-zero exit codes manually
                capture_output=True,
                text=True,
            )
            if process.returncode == 0:
                status_var.set(f"Finished: {os.path.basename(script_full_path)}")
            else:
                error_msg = process.stderr.strip() if process.stderr else "Unknown PS error"
                status_var.set(f"PS Script Failed: {os.path.basename(script_full_path)}. Error: {error_msg[:100]}...")
                print(f"Error running {script_full_path}:\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}")

        else: # Python scripts
            print(f"Launching Python script: {sys.executable} {script_full_path}")
            if is_python_gui:
                # Launch GUI and don't wait (Popen)
                subprocess.Popen([sys.executable, script_full_path])
                status_var.set(f"Launched GUI: {os.path.basename(script_full_path)}")
            else:
                # For CLI Python scripts, run and wait to see output/errors
                process = subprocess.run(
                    [sys.executable, script_full_path],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if process.returncode == 0:
                     status_var.set(f"Python script finished: {os.path.basename(script_full_path)}")
                else:
                    error_msg = process.stderr.strip() if process.stderr else "Unknown Python error"
                    status_var.set(f"Python Script Failed: {os.path.basename(script_full_path)}. Error: {error_msg[:100]}...")
                print(f"Output from {script_full_path}:\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}")


    except FileNotFoundError:
        status_var.set(f"Error: Executable (Python/PowerShell) not found for {script_full_path}")
        print(f"Error: Executable not found for {script_full_path}")
    except Exception as e:
        status_var.set(f"Error launching {os.path.basename(script_full_path)}: {e}")
        print(f"Exception launching {script_full_path}: {e}")

# --- Specific Launch Functions ---
def launch_password_recovery():
    # This is breached_email_checker/main.py
    script_rel_path = os.path.join("breached_email_checker", "main.py")
    launch_tool(script_rel_path, is_python_gui=False) # It's a CLI script

def launch_vt_file_scanner():
    script_rel_path = "Scan-FilesVT_CLI.py"
    launch_tool(script_rel_path, is_python_gui=True)

def launch_email_checker_gui():
    script_rel_path = os.path.join("breached_email_checker", "script_gui.py")
    launch_tool(script_rel_path, is_python_gui=True)

def launch_malicious_url_scanner():
    script_rel_path = "MaliciousBrowserHistory.ps1"
    launch_tool(script_rel_path, use_powershell=True, needs_admin=True)

def launch_wpa_checker():
    script_rel_path = "wpa_check.ps1"
    launch_tool(script_rel_path, use_powershell=True, needs_admin=True)

# Global variable to track the web server
_web_server = None
_web_server_port = 8000

def start_local_server():
    """Starts a local HTTP server to serve the HTML files."""
    global _web_server, _web_server_port
    if _web_server is not None:
        try:
            # Check if server is still running
            _web_server.server_address
            return _web_server_port
        except:
            _web_server = None  # Server died, restart it
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=base_dir, **kwargs)
        
        def log_message(self, format, *args):
            # Suppress server logs
            pass
        
        def end_headers(self):
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            super().end_headers()
    
    try:
        # Try to find an available port
        port = _web_server_port
        for _ in range(10):  # Try up to 10 ports
            try:
                handler = CustomHTTPRequestHandler
                _web_server = socketserver.TCPServer(("", port), handler)
                _web_server.allow_reuse_address = True
                _web_server_port = port  # Update global port
                break
            except OSError:
                port += 1
        else:
            raise Exception("Could not find an available port")
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=_web_server.serve_forever, daemon=True)
        server_thread.start()
        time.sleep(1)  # Give server more time to start
        
        return port
    except Exception as e:
        print(f"Error starting web server: {e}")
        import traceback
        traceback.print_exc()
        return None

def open_report_viewer():
    """Opens the HTML report viewer in the default browser using a local web server."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "index.html")
    
    if not os.path.exists(index_path):
        messagebox.showerror("Error", f"Report viewer not found at {index_path}")
        status_var.set("Error: Report viewer not found")
        return
    
    # Start local web server
    port = start_local_server()
    if port is None:
        # Fallback to file:// protocol with warning
        index_url = f"file:///{index_path.replace(os.sep, '/')}"
        webbrowser.open(index_url)
        messagebox.showwarning(
            "CORS Warning", 
            "Report viewer opened, but some features may not work due to browser security restrictions.\n\n"
            "For full functionality, please:\n"
            "1. Open Command Prompt in the project folder\n"
            "2. Run: python -m http.server 8000\n"
            "3. Open: http://localhost:8000/index.html"
        )
        status_var.set("Report viewer opened (limited functionality)")
    else:
        index_url = f"http://localhost:{port}/index.html"
        webbrowser.open(index_url)
        status_var.set(f"Report viewer opened at http://localhost:{port}")

def open_output_folder():
    """Opens the output folder in Windows Explorer."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    if os.path.exists(output_dir):
        os.startfile(output_dir)
        status_var.set("Output folder opened")
    else:
        messagebox.showwarning("Warning", f"Output folder not found at {output_dir}")
        status_var.set("Warning: Output folder not found")

def export_all_reports():
    """Export all reports to ZIP file."""
    if not MODULES_AVAILABLE:
        messagebox.showinfo("Info", "Export functionality requires additional modules.\nInstall: pip install reportlab beautifulsoup4")
        return
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    
    if not os.path.exists(output_dir):
        messagebox.showwarning("Warning", "No output folder found. Run collectors first.")
        return
    
    try:
        zip_file = export_all_reports_to_zip(output_dir)
        if zip_file:
            messagebox.showinfo("Success", f"All reports exported to:\n{zip_file}")
            status_var.set(f"Reports exported to {os.path.basename(zip_file)}")
            # Open the folder containing the ZIP
            os.startfile(os.path.dirname(os.path.abspath(zip_file)))
        else:
            messagebox.showerror("Error", "Failed to create ZIP file.")
    except Exception as e:
        messagebox.showerror("Error", f"Export failed: {e}")
        status_var.set(f"Export error: {e}")

def archive_reports():
    """Archive current reports."""
    if not MODULES_AVAILABLE or not archiver:
        messagebox.showinfo("Info", "Archive functionality requires configuration module.")
        return
    
    try:
        archive_path = archiver.archive_current_reports()
        if archive_path:
            messagebox.showinfo("Success", f"Reports archived to:\n{archive_path}")
            status_var.set("Reports archived successfully")
        else:
            messagebox.showwarning("Warning", "Archive disabled in settings or failed.")
    except Exception as e:
        messagebox.showerror("Error", f"Archive failed: {e}")

def view_alerts():
    """View security alerts."""
    if not MODULES_AVAILABLE or not alert_system:
        messagebox.showinfo("Info", "Alert system requires configuration module.")
        return
    
    try:
        unack_alerts = alert_system.get_unacknowledged_alerts()
        if not unack_alerts:
            messagebox.showinfo("No Alerts", "No unacknowledged alerts found.")
            return
        
        # Create a simple alert viewer window
        alert_window = ttk.Toplevel(root)
        alert_window.title("Security Alerts")
        alert_window.geometry("700x500")
        
        alert_frame = ttk.Frame(alert_window, padding=10)
        alert_frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(alert_frame, text=f"Security Alerts ({len(unack_alerts)})", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Alert list
        alert_listbox = Listbox(alert_frame, font=("Arial", 10), height=15)
        alert_listbox.pack(fill=BOTH, expand=True, pady=5)
        
        for alert in unack_alerts:
            severity_icon = "🔴" if alert.get("severity") == "high" else "🟡" if alert.get("severity") == "medium" else "🟢"
            alert_text = f"{severity_icon} [{alert.get('severity', 'unknown').upper()}] {alert.get('title', 'Alert')}"
            alert_listbox.insert("end", alert_text)
        
        def acknowledge_selected():
            selection = alert_listbox.curselection()
            if selection:
                alert_system.acknowledge_alert(selection[0])
                alert_listbox.delete(selection[0])
                messagebox.showinfo("Success", "Alert acknowledged.")
        
        ttk.Button(alert_frame, text="Acknowledge Selected", 
                  command=acknowledge_selected, bootstyle=SUCCESS).pack(pady=5)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load alerts: {e}")

# --- Main Application Setup ---
root = ttk.Window(themename="cyborg")
root.title("ForensiQ - Windows Forensics Toolkit")
root.geometry("1200x900")
root.minsize(1000, 700)

# Modern header with gradient effect
header_frame = ttk.Frame(root, style="primary.TFrame")
header_frame.pack(fill=X, pady=(0, 10))

header_content = ttk.Frame(header_frame, padding=20)
header_content.pack(fill=X)

# Title section
title_frame = ttk.Frame(header_content)
title_frame.pack(side=LEFT, fill=BOTH, expand=True)

title_label = ttk.Label(
    title_frame, 
    text="ForensiQ", 
    font=("Segoe UI", 32, "bold"),
    foreground="#00d4ff"
)
title_label.pack(anchor="w")

subtitle_label = ttk.Label(
    title_frame, 
    text="Professional Windows Forensics & Security Analysis Platform", 
    font=("Segoe UI", 11),
    foreground="#b0b0b0"
)
subtitle_label.pack(anchor="w", pady=(2, 0))

# Status indicator in header
status_indicator_frame = ttk.Frame(header_content)
status_indicator_frame.pack(side=RIGHT, padx=10)

admin_status_label = ttk.Label(
    status_indicator_frame,
    text="🔒 Admin",
    font=("Segoe UI", 10, "bold"),
    foreground="#28a745"
)
admin_status_label.pack()

# --- Main Container ---
main_container = ttk.Frame(root, padding=15)
main_container.pack(fill=BOTH, expand=True)

# --- PowerShell Collectors Section ---
collectors_card = ttk.LabelFrame(
    main_container, 
    text="📊 Data Collection Scripts", 
    padding=15,
    bootstyle="info"
)
collectors_card.pack(fill=BOTH, expand=True, pady=(0, 10))

# Search and filter frame
search_frame = ttk.Frame(collectors_card)
search_frame.pack(fill=X, pady=(0, 15))

search_label = ttk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 10))
search_label.pack(side=LEFT, padx=(0, 5))

search_var = StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 10), width=30)
search_entry.pack(side=LEFT, padx=5, fill=X, expand=True)

select_all_var = BooleanVar()
select_all_cb = ttk.Checkbutton(
    search_frame, 
    text="Select All", 
    variable=select_all_var,
    bootstyle="round-toggle"
)
select_all_cb.pack(side=RIGHT, padx=5)

# Scrollable checkbox frame
checkbox_container = ttk.Frame(collectors_card)
checkbox_container.pack(fill=BOTH, expand=True, pady=(0, 10))

# Create canvas with scrollbar for modern scrolling
canvas_frame = ttk.Frame(checkbox_container)
canvas_frame.pack(fill=BOTH, expand=True)

canvas = Canvas(canvas_frame, highlightthickness=0, bg="#1a1a1a")
scrollbar_v = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=canvas.yview)
scrollable_frame = Frame(canvas, bg="#1a1a1a")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar_v.set)

canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar_v.pack(side=RIGHT, fill=Y)

# Mousewheel scrolling (Windows and Linux)
def on_mousewheel(event):
    if sys.platform == "win32":
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    else:
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

if sys.platform == "win32":
    canvas.bind_all("<MouseWheel>", on_mousewheel)
else:
    canvas.bind_all("<Button-4>", on_mousewheel)
    canvas.bind_all("<Button-5>", on_mousewheel)

# Store checkbox variables
checkbox_vars = []
checkbox_widgets = []

def filter_scripts(*args):
    """Filter scripts based on search term."""
    search_term = search_var.get().lower()
    for i, (widget, var, script) in enumerate(zip(checkbox_widgets, checkbox_vars, ps_scripts)):
        if search_term in script.lower():
            widget.pack(fill=X, pady=2, padx=5)
        else:
            widget.pack_forget()

def toggle_select_all():
    """Select or deselect all visible checkboxes."""
    state = select_all_var.get()
    search_term = search_var.get().lower()
    for var, script in zip(checkbox_vars, ps_scripts):
        if search_term in script.lower() or not search_term:
            var.set(state)

select_all_var.trace("w", lambda *args: toggle_select_all())
search_var.trace("w", filter_scripts)

# Create checkboxes for each script
for script in ps_scripts:
    var = BooleanVar()
    checkbox_vars.append(var)
    
    # Create modern checkbox with better styling
    cb_frame = Frame(scrollable_frame, bg="#1a1a1a")
    cb_frame.pack(fill=X, pady=2, padx=5)
    
    cb = ttk.Checkbutton(
        cb_frame,
        text=script,
        variable=var,
        bootstyle="round-toggle"
    )
    cb.pack(side=LEFT, anchor="w")
    
    checkbox_widgets.append(cb_frame)

# Action buttons frame
ps_button_frame = ttk.Frame(collectors_card)
ps_button_frame.pack(fill=X, pady=(10, 0))

selected_count_label = ttk.Label(
    ps_button_frame,
    text="0 selected",
    font=("Segoe UI", 9),
    foreground="#888"
)
selected_count_label.pack(side=LEFT, padx=(0, 10))

def update_selected_count():
    count = sum(1 for var in checkbox_vars if var.get())
    selected_count_label.config(text=f"{count} selected")
    if count > 0:
        selected_count_label.config(foreground="#00d4ff")
    else:
        selected_count_label.config(foreground="#888")

# Update count when checkboxes change
for var in checkbox_vars:
    var.trace("w", lambda *args: update_selected_count())

# Initialize count
update_selected_count()

btn_run_selected = ttk.Button(
    ps_button_frame,
    text="▶ Run Selected",
    command=run_selected_collectors,
    bootstyle="success",
    width=20
)
btn_run_selected.pack(side=LEFT, padx=5)

btn_run_all = ttk.Button(
    ps_button_frame,
    text="▶▶ Run All",
    command=run_all_collectors,
    bootstyle="primary",
    width=20
)
btn_run_all.pack(side=LEFT, padx=5)

def select_all_scripts():
    for var in checkbox_vars:
        var.set(True)
    select_all_var.set(True)

btn_select_all = ttk.Button(
    ps_button_frame,
    text="✓ Select All",
    command=select_all_scripts,
    bootstyle="secondary-outline",
    width=15
)
btn_select_all.pack(side=LEFT, padx=5)

def clear_selection():
    for var in checkbox_vars:
        var.set(False)
    select_all_var.set(False)

btn_clear = ttk.Button(
    ps_button_frame,
    text="✗ Clear",
    command=clear_selection,
    bootstyle="secondary-outline",
    width=15
)
btn_clear.pack(side=LEFT, padx=5)

# --- Quick Actions Section ---
quick_actions_card = ttk.LabelFrame(
    main_container,
    text="⚡ Quick Actions",
    padding=15,
    bootstyle="secondary"
)
quick_actions_card.pack(fill=X, pady=(0, 10))

quick_actions_grid = ttk.Frame(quick_actions_card)
quick_actions_grid.pack(fill=X)

# Configure grid columns
for i in range(5):
    quick_actions_grid.columnconfigure(i, weight=1, uniform="quick_actions")

btn_view_reports = ttk.Button(
    quick_actions_grid,
    text="📊 View Reports",
    command=open_report_viewer,
    bootstyle="info-outline",
    width=18
)
btn_view_reports.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

btn_output_folder = ttk.Button(
    quick_actions_grid,
    text="📁 Output Folder",
    command=open_output_folder,
    bootstyle="info-outline",
    width=18
)
btn_output_folder.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

btn_export_all = ttk.Button(
    quick_actions_grid,
    text="📦 Export All",
    command=export_all_reports,
    bootstyle="success-outline",
    width=18
)
btn_export_all.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

btn_archive = ttk.Button(
    quick_actions_grid,
    text="📚 Archive",
    command=archive_reports,
    bootstyle="warning-outline",
    width=18
)
btn_archive.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

if MODULES_AVAILABLE:
    btn_alerts = ttk.Button(
        quick_actions_grid,
        text="⚠️ Alerts",
        command=view_alerts,
        bootstyle="danger-outline",
        width=18
    )
    btn_alerts.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

# --- Additional Tools Section ---
tools_card = ttk.LabelFrame(
    main_container,
    text="🛠️ Advanced Tools & Scanners",
    padding=15,
    bootstyle="warning"
)
tools_card.pack(fill=X, pady=(0, 10))

tools_grid = ttk.Frame(tools_card)
tools_grid.pack(fill=X)

# Configure grid columns
for i in range(3):
    tools_grid.columnconfigure(i, weight=1, uniform="tools")

btn_pass_rec = ttk.Button(
    tools_grid,
    text="🔑 Browser Passwords",
    command=launch_password_recovery,
    bootstyle="info",
    width=25
)
btn_pass_rec.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

btn_vt_scan = ttk.Button(
    tools_grid,
    text="🛡️ VirusTotal Scanner",
    command=launch_vt_file_scanner,
    bootstyle="info",
    width=25
)
btn_vt_scan.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

btn_email_check = ttk.Button(
    tools_grid,
    text="📧 Email Breach Check",
    command=launch_email_checker_gui,
    bootstyle="info",
    width=25
)
btn_email_check.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

btn_url_scan = ttk.Button(
    tools_grid,
    text="🌐 Browser History Scan",
    command=launch_malicious_url_scanner,
    bootstyle="warning-outline",
    width=25
)
btn_url_scan.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

btn_wpa_check = ttk.Button(
    tools_grid,
    text="📶 Wi-Fi Security Check",
    command=launch_wpa_checker,
    bootstyle="warning-outline",
    width=25
)
btn_wpa_check.grid(row=1, column=1, padx=5, pady=5, sticky="ew")


# --- Status Bar (Bottom) ---
status_bar = ttk.Frame(root, style="secondary.TFrame", padding=10)
status_bar.pack(fill=X, side=BOTTOM)

status_var = StringVar(value="Ready - Select scripts to run or launch a tool")
status_label = ttk.Label(
    status_bar,
    textvariable=status_var,
    font=("Segoe UI", 9),
    foreground="#b0b0b0"
)
status_label.pack(side=LEFT, padx=(0, 10), fill=X, expand=True)

progress_bar = ttk.Progressbar(
    status_bar,
    orient=HORIZONTAL,
    length=250,
    mode='determinate',
    bootstyle="success-striped"
)
progress_bar.pack(side=RIGHT, padx=(10, 0))

# --- Footer Actions ---
footer_frame = ttk.Frame(root, padding=(15, 5, 15, 10))
footer_frame.pack(fill=X, side=BOTTOM)

left_footer = ttk.Frame(footer_frame)
left_footer.pack(side=LEFT, fill=X, expand=True)

if MODULES_AVAILABLE:
    def show_settings():
        settings_window = ttk.Toplevel(root)
        settings_window.title("ForensiQ Settings")
        settings_window.geometry("550x450")
        settings_window.resizable(False, False)
        
        # Center window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (450 // 2)
        settings_window.geometry(f"550x450+{x}+{y}")
        
        settings_frame = ttk.Frame(settings_window, padding=25)
        settings_frame.pack(fill=BOTH, expand=True)
        
        title_label = ttk.Label(
            settings_frame,
            text="⚙️ ForensiQ Settings",
            font=("Segoe UI", 20, "bold"),
            foreground="#00d4ff"
        )
        title_label.pack(pady=(0, 20))
        
        # Theme setting
        theme_frame = ttk.LabelFrame(settings_frame, text="Appearance", padding=15)
        theme_frame.pack(fill=X, pady=5)
        theme_var = StringVar(value=config_manager.get_setting("theme", "dark") if config_manager else "dark")
        ttk.Radiobutton(theme_frame, text="Dark Theme", variable=theme_var, value="dark", bootstyle="info-round-toggle").pack(anchor="w", pady=2)
        ttk.Radiobutton(theme_frame, text="Light Theme", variable=theme_var, value="light", bootstyle="info-round-toggle").pack(anchor="w", pady=2)
        
        # Alert settings
        alert_frame = ttk.LabelFrame(settings_frame, text="Alerts", padding=15)
        alert_frame.pack(fill=X, pady=5)
        alert_enabled = ttk.BooleanVar(value=config_manager.get_setting("enable_alerts", True) if config_manager else True)
        ttk.Checkbutton(alert_frame, text="Enable Security Alerts", variable=alert_enabled, bootstyle="round-toggle").pack(anchor="w", pady=2)
        
        # Archive settings
        archive_frame = ttk.LabelFrame(settings_frame, text="Archiving", padding=15)
        archive_frame.pack(fill=X, pady=5)
        archive_enabled = ttk.BooleanVar(value=config_manager.get_setting("archive_reports", True) if config_manager else True)
        ttk.Checkbutton(archive_frame, text="Auto-archive reports", variable=archive_enabled, bootstyle="round-toggle").pack(anchor="w", pady=2)
        
        def save_settings():
            if config_manager:
                config_manager.set_setting("theme", theme_var.get())
                config_manager.set_setting("enable_alerts", alert_enabled.get())
                config_manager.set_setting("archive_reports", archive_enabled.get())
                messagebox.showinfo("Success", "Settings saved successfully!")
                settings_window.destroy()
            else:
                messagebox.showwarning("Warning", "Configuration system not available.")
        
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=X, pady=(15, 0))
        
        ttk.Button(button_frame, text="Save Settings", command=save_settings, bootstyle="success", width=20).pack(side=RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy, bootstyle="secondary-outline", width=20).pack(side=RIGHT, padx=5)
    
    btn_settings = ttk.Button(
        left_footer,
        text="⚙️ Settings",
        command=show_settings,
        bootstyle="secondary-outline",
        width=15
    )
    btn_settings.pack(side=LEFT, padx=5)

right_footer = ttk.Frame(footer_frame)
right_footer.pack(side=RIGHT)

btn_exit = ttk.Button(
    right_footer,
    text="Exit",
    command=root.quit,
    bootstyle="danger",
    width=12
)
btn_exit.pack(side=RIGHT, padx=5)


# Initialize configuration and systems
config_manager = None
alert_system = None
archiver = None

if MODULES_AVAILABLE:
    try:
        config_manager = ConfigManager()
        alert_system = AlertSystem(config_manager)
        archiver = ReportArchiver(config_manager)
        print("Configuration and alert systems initialized.")
    except Exception as e:
        print(f"Warning: Could not initialize advanced features: {e}")

# --- Initial Actions ---
if __name__ == "__main__":
    # Check for Admin rights if on Windows (Optional but good for UX)
    if sys.platform == "win32":
        try:
            # Use ctypes to check for admin privileges on Windows
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                print("Running with Administrator privileges.")
                admin_status_label.config(text="🔒 Admin", foreground="#28a745")
                status_var.set("✅ Running with Administrator privileges")
            else:
                print("WARNING: Not running with Administrator privileges. Some tools/collectors may fail or provide incomplete data.")
                admin_status_label.config(text="⚠️ Not Admin", foreground="#ffc107")
                status_var.set("⚠️ WARNING: Not running as Administrator. Some tools may fail.")
        except Exception as e:
            # Fallback method using net session
            try:
                subprocess.check_output("net session", stderr=subprocess.STDOUT, shell=True, timeout=2)
                is_admin = True
                print("Running with Administrator privileges.")
                admin_status_label.config(text="🔒 Admin", foreground="#28a745")
                status_var.set("✅ Running with Administrator privileges")
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                is_admin = False
                print("WARNING: Could not determine admin status. Some tools may require admin privileges.")
                admin_status_label.config(text="❓ Unknown", foreground="#ffc107")
                status_var.set("⚠️ WARNING: Admin status unknown. Some tools may fail.")

    generate_manifest()
    root.mainloop()
