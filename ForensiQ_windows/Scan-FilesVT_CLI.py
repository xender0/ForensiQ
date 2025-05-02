import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import hashlib
import os
import requests
import time
import threading
import queue

# --- Configuration ---
VT_API_URL_BASE = "https://www.virustotal.com/api/v3/files/"
# Approx 4 requests/min for free tier. Sleep slightly more than 15s.
RATE_LIMIT_SLEEP_SECONDS = 16
# Store results to avoid re-querying during a single session
vt_results_cache = {}
# Queue for thread communication
update_queue = queue.Queue()

# --- Core Functions ---

def calculate_sha256(filepath):
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (IOError, PermissionError) as e:
        # Send error back to main thread via queue (Corrected format)
        update_queue.put(
            (
                "status",
                (f"Error hashing {os.path.basename(filepath)}: {e}", "error"),
            )
        )
        return None

def query_virus_total_hash(file_hash, api_key):
    """Queries VirusTotal API for a given file hash."""
    if not api_key:
        # Corrected format
        update_queue.put(("status", ("API Key is missing!", "error")))
        return {"status": "Error", "error": "API Key Missing"}

    if file_hash in vt_results_cache:
        # Corrected format
        update_queue.put(
            ("status", (f"Using cached result for {file_hash[:10]}...", "info"))
        )
        return vt_results_cache[file_hash]

    api_url = f"{VT_API_URL_BASE}{file_hash}"
    headers = {"x-apikey": api_key}

    # Corrected format
    update_queue.put(
        ("status", (f"Querying VT for {file_hash[:10]}...", "info"))
    )

    try:
        # Rate Limiting
        time.sleep(RATE_LIMIT_SLEEP_SECONDS)

        response = requests.get(api_url, headers=headers, timeout=30) # Added timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        undetected = stats.get("undetected", 0)
        total_engines = malicious + suspicious + undetected
        if total_engines == 0 and data.get("last_analysis_results"):
             # Fallback if stats are zero but results exist
             total_engines = len(data.get("last_analysis_results", {}))

        vt_link = f"https://www.virustotal.com/gui/file/{file_hash}"
        meaningful_name = data.get("meaningful_name", "-")

        result = {
            "status": "Checked",
            "malicious": malicious,
            "suspicious": suspicious,
            "total_engines": total_engines,
            "link": vt_link,
            "name": meaningful_name,
            "error": None,
        }
        vt_results_cache[file_hash] = result # Cache success
        return result

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_message = f"HTTP {status_code}"
        status = "Error"
        if status_code == 404:
            error_message = "Hash not found on VT"
            status = "Unknown"
            result = {
                "status": status, "error": error_message, "malicious": 0,
                "suspicious": 0, "total_engines": 0, "link": "-", "name": "-"
            }
            vt_results_cache[file_hash] = result # Cache unknown state
            # Corrected format
            update_queue.put(
                ("status", (f"Hash {file_hash[:10]}... not found on VT.", "warn"))
            )
            return result
        elif status_code == 429:
             error_message = "Rate limit exceeded"
             status = "Rate Limited"
             # Corrected format
             update_queue.put(("status", ("VirusTotal API rate limit likely exceeded.", "error")))
        else:
            # Corrected format
            update_queue.put(("status", (f"VT API Error for {file_hash[:10]}...: {e}", "error")))

        result = {"status": status, "error": error_message}
        # Don't cache generic errors, maybe transient
        return result

    except requests.exceptions.RequestException as e:
        # Corrected format
        update_queue.put(("status", (f"Network Error querying VT: {e}", "error")))
        return {"status": "Error", "error": "Network Error"}
    except Exception as e:
        # Corrected format
        update_queue.put(("status", (f"Unexpected error querying VT: {e}", "error")))
        return {"status": "Error", "error": "Unexpected Error"}


def process_files_thread(file_paths, api_key):
    """Worker thread function to process files."""
    total_files = len(file_paths)
    processed_count = 0
    unique_hashes = set()
    file_hash_map = {} # Store {filepath: hash}

    # --- Hashing Phase ---
    # Corrected format
    update_queue.put(("status", ("Starting hashing phase...", "info")))
    for filepath in file_paths:
        processed_count += 1
        # Corrected format
        update_queue.put(
            (
                "status",
                (f"Hashing ({processed_count}/{total_files}): {os.path.basename(filepath)}", "info"),
            )
        )
        file_hash = calculate_sha256(filepath)
        if file_hash:
            unique_hashes.add(file_hash)
            file_hash_map[filepath] = file_hash
        else:
            # Error already sent by calculate_sha256
            # Put result placeholder for hash error
            update_queue.put(("result", (filepath, "HASH_ERROR", "Error hashing file", "-", "-", "error")))

    # --- VT Query Phase ---
    # Corrected format
    update_queue.put(("status", (f"Querying VT for {len(unique_hashes)} unique hashes...", "info")))
    hash_results = {} # Store {hash: vt_result}
    processed_hash_count = 0
    total_unique = len(unique_hashes)

    for h in unique_hashes:
        processed_hash_count += 1
        # Corrected format
        update_queue.put(
            (
                "status",
                (f"Querying VT ({processed_hash_count}/{total_unique}): {h[:10]}...", "info"),
            )
        )
        result = query_virus_total_hash(h, api_key)
        hash_results[h] = result
        if result.get("status") == "Rate Limited":
            # Corrected format
            update_queue.put(("status", ("Stopping due to rate limit.", "error")))
            break # Stop querying if rate limited

    # --- Update Results Table ---
    # Corrected format
    update_queue.put(("status", ("Updating results table...", "info")))
    for filepath, file_hash in file_hash_map.items():
        if file_hash in hash_results:
            vt_result = hash_results[file_hash]
            status = vt_result.get("status", "Error")
            detections = "-"
            link = vt_result.get("link", "-")
            tag = "normal" # Default tag

            if status == "Checked":
                malicious = vt_result.get("malicious", 0)
                suspicious = vt_result.get("suspicious", 0)
                total = vt_result.get("total_engines", 0)
                if malicious > 0:
                    status = "MALICIOUS"
                    detections = f"{malicious}/{total}"
                    tag = "malicious"
                elif suspicious > 0:
                    status = "SUSPICIOUS"
                    detections = f"{suspicious} suspicious"
                    tag = "suspicious"
                else:
                    status = "Clean"
                    detections = f"0/{total}"
                    tag = "clean"
            elif status == "Unknown":
                 tag = "unknown"
            elif status == "Rate Limited":
                 tag = "error"
                 detections = "Rate Limited"
            else: # Error during VT query
                status = f"Error ({vt_result.get('error', '')})"
                tag = "error"

            update_queue.put(
                ("result", (filepath, file_hash, status, detections, link, tag))
            )
        elif file_hash: # Hash calculated but VT query might have been skipped (e.g. rate limit)
             update_queue.put(
                ("result", (filepath, file_hash, "Not Checked (Rate Limit?)", "-", "-", "error"))
            )
        # else: Hash error already handled during hashing phase

    # Corrected format
    update_queue.put(("status", ("Scan finished.", "done")))
    update_queue.put(("enable_scan_button", True))


# --- GUI Functions ---

def add_files():
    """Opens file dialog and adds selected files to the list."""
    filenames = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=(("All files", "*.*"),) # Add more specific types if needed
    )
    current_files = set(listbox_files.get(0, tk.END))
    added_count = 0
    for f in filenames:
        if f not in current_files:
            listbox_files.insert(tk.END, f)
            added_count += 1
    update_status(f"Added {added_count} new file(s).")

def remove_selected():
    """Removes selected files from the listbox."""
    selected_indices = listbox_files.curselection()
    # Remove in reverse order to avoid index shifting issues
    for i in reversed(selected_indices):
        listbox_files.delete(i)
    update_status(f"Removed {len(selected_indices)} file(s).")

def clear_list():
    """Clears all files from the listbox."""
    listbox_files.delete(0, tk.END)
    update_status("File list cleared.")

def start_scan():
    """Starts the file scanning process in a separate thread."""
    api_key = entry_api_key.get().strip()
    if not api_key:
        messagebox.showerror("API Key Missing", "Please enter your VirusTotal API Key.")
        return

    file_paths = listbox_files.get(0, tk.END)
    if not file_paths:
        messagebox.showwarning("No Files", "Please add files to scan first.")
        return

    # Clear previous results and cache
    for item in tree_results.get_children():
        tree_results.delete(item)
    vt_results_cache.clear()

    update_status("Starting scan...", "info")
    scan_button.config(state=DISABLED)

    # Start the worker thread
    scan_thread = threading.Thread(
        target=process_files_thread,
        args=(file_paths, api_key),
        daemon=True # Allows main program to exit even if thread is running
    )
    scan_thread.start()

def update_status(message, level="info"):
    """Updates the status bar label."""
    status_label.config(text=f"Status: {message}")
    if level == "error":
        status_label.config(bootstyle="danger")
    elif level == "warn":
        status_label.config(bootstyle="warning")
    elif level == "done":
        status_label.config(bootstyle="success")
    else: # info
        status_label.config(bootstyle="primary") # Or default style

def process_queue():
    """Processes messages from the update queue."""
    try:
        while True:
            # Expecting a 2-element tuple: (message_type, data_payload)
            message_type, data_payload = update_queue.get_nowait()

            if message_type == "status":
                # data_payload should be a tuple: (message_text, level)
                if isinstance(data_payload, (list, tuple)) and len(data_payload) == 2:
                    update_status(data_payload[0], data_payload[1])
                else:
                    # Log if data format is wrong, but don't crash
                    print(f"Warning: Received malformed status update: {data_payload}")
                    update_status(str(data_payload), "error") # Show something in status

            elif message_type == "result":
                # data_payload should be a tuple: (filepath, hash, status, detections, link, tag)
                if isinstance(data_payload, (list, tuple)) and len(data_payload) == 6:
                    filepath, file_hash, status, detections, link, tag = data_payload
                    tree_results.insert(
                        "",
                        tk.END,
                        values=(
                            os.path.basename(filepath), # Show only filename
                            filepath, # Full path for reference/tooltip maybe later
                            file_hash[:12] + "..." if file_hash != "HASH_ERROR" else "HASH_ERROR", # Shortened hash or error
                            status,
                            detections,
                            link,
                        ),
                        tags=(tag,) # Apply the tag for coloring
                    )
                    # Auto-scroll to the bottom
                    tree_results.yview_moveto(1)
                else:
                     print(f"Warning: Received malformed result update: {data_payload}")

            elif message_type == "enable_scan_button":
                 # data_payload should be True
                 if data_payload:
                     scan_button.config(state=NORMAL)

    except queue.Empty:
        # No more messages in the queue right now
        pass
    finally:
        # Schedule the next check
        root.after(100, process_queue)


# --- GUI Setup ---
root = ttk.Window(themename="darkly") # Use a dark theme
root.title("VirusTotal File Scanner")
root.geometry("900x700")

# --- Top Frame: API Key ---
frame_top = ttk.Frame(root, padding=10)
frame_top.pack(fill=X)
ttk.Label(frame_top, text="VirusTotal API Key:").pack(side=LEFT, padx=5)
entry_api_key = ttk.Entry(frame_top, width=60, show="*") # Mask API key
entry_api_key.pack(side=LEFT, fill=X, expand=True, padx=5)

# --- Middle Frame: File List and Controls ---
frame_middle = ttk.Frame(root, padding=10)
frame_middle.pack(fill=BOTH, expand=True)

# Controls Sub-Frame
frame_controls = ttk.Frame(frame_middle)
frame_controls.pack(fill=X, pady=(0, 10))
btn_add = ttk.Button(frame_controls, text="Add Files", command=add_files, bootstyle=SUCCESS)
btn_add.pack(side=LEFT, padx=5)
btn_remove = ttk.Button(frame_controls, text="Remove Selected", command=remove_selected, bootstyle=WARNING)
btn_remove.pack(side=LEFT, padx=5)
btn_clear = ttk.Button(frame_controls, text="Clear List", command=clear_list, bootstyle=DANGER)
btn_clear.pack(side=LEFT, padx=5)

# File Listbox Sub-Frame
frame_list = ttk.Frame(frame_middle)
frame_list.pack(fill=BOTH, expand=True)
list_scrollbar = ttk.Scrollbar(frame_list, orient=VERTICAL)
listbox_files = tk.Listbox(
    frame_list,
    selectmode=tk.EXTENDED, # Allow multiple selections
    yscrollcommand=list_scrollbar.set,
    height=8 # Adjust height as needed
)
list_scrollbar.config(command=listbox_files.yview)
list_scrollbar.pack(side=RIGHT, fill=Y)
listbox_files.pack(side=LEFT, fill=BOTH, expand=True)

# --- Scan Button ---
scan_button = ttk.Button(root, text="Scan Selected Files", command=start_scan, bootstyle=(PRIMARY, OUTLINE))
scan_button.pack(pady=10)

# --- Bottom Frame: Results Treeview ---
frame_results = ttk.LabelFrame(root, text="Scan Results", padding=10)
frame_results.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

results_cols = ("filename", "fullpath", "hash", "status", "detections", "link")
tree_results = ttk.Treeview(
    frame_results,
    columns=results_cols,
    show="headings", # Don't show the first empty column
    height=10,
    bootstyle="primary"
)

# Define headings
tree_results.heading("filename", text="File Name")
tree_results.heading("fullpath", text="Full Path")
tree_results.heading("hash", text="Hash (SHA256)")
tree_results.heading("status", text="Status")
tree_results.heading("detections", text="Detections")
tree_results.heading("link", text="VT Link")

# Define column widths and hide fullpath initially (can be shown if needed)
tree_results.column("filename", width=180, anchor=W)
tree_results.column("fullpath", width=0, stretch=NO) # Hide full path column
tree_results.column("hash", width=120, anchor=W)
tree_results.column("status", width=100, anchor=W)
tree_results.column("detections", width=100, anchor=W)
tree_results.column("link", width=150, anchor=W)

# Add scrollbars for results
results_ysb = ttk.Scrollbar(frame_results, orient=VERTICAL, command=tree_results.yview)
results_xsb = ttk.Scrollbar(frame_results, orient=HORIZONTAL, command=tree_results.xview)
tree_results.configure(yscrollcommand=results_ysb.set, xscrollcommand=results_xsb.set)

results_ysb.pack(side=RIGHT, fill=Y)
results_xsb.pack(side=BOTTOM, fill=X)
tree_results.pack(fill=BOTH, expand=True)

# Configure tags for coloring rows
tree_results.tag_configure("malicious", background="#dc3545", foreground="white") # Danger color
tree_results.tag_configure("suspicious", background="#ffc107", foreground="black") # Warning color
tree_results.tag_configure("clean", background="#198754", foreground="white") # Success color (subtle)
tree_results.tag_configure("unknown", background="#6c757d", foreground="white") # Secondary color
tree_results.tag_configure("error", background="#adb5bd", foreground="black") # Light color for errors
tree_results.tag_configure("normal", background="", foreground="") # Default/Normal tag

# --- Status Bar ---
status_label = ttk.Label(root, text="Status: Idle", padding=5, bootstyle=PRIMARY, anchor=W)
status_label.pack(side=BOTTOM, fill=X)

# --- Start Queue Processor ---
root.after(100, process_queue)

# --- Run GUI ---
root.mainloop()
