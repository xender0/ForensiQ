import os
import sys
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as msgbox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import time
import re
import requests
import csv
from queue import Queue
from queue import Empty
import json
import traceback # Added for better error reporting

LEAKCHECK_API_URL = "https://leakcheck.io/api/public?check={email}&type=email"
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
REQUEST_DELAY_SECONDS = 1.0

def check_email_leak_api(email: str) -> tuple[int, any]:
    """
    Checks a single email against the LeakCheck.io public API.

    Returns:
        tuple: (status_code, data_or_error_msg)
               - (200, json_data) : Success
               - (429, retry_after_seconds) : Rate Limited
               - (other_status, error_message) : API or other HTTP error
               - (600, error_message) : Network or request error
    """
    url = LEAKCHECK_API_URL.format(email=email)
    try:
        response = requests.get(url, timeout=20)

        if response.status_code == 200:
            try:
                data = response.json()
                return (200, data)
            except json.JSONDecodeError:
                return (500, "Invalid JSON response from API")
        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After', '60')
            try:
                wait_time = int(retry_after)
            except ValueError:
                wait_time = 60
            return (429, wait_time)
        else:
            # Try to get more info from the response body if possible
            error_detail = response.text[:200] # Limit length
            return (response.status_code, f"API Error: {response.status_code} - {error_detail}")

    except requests.exceptions.Timeout:
        return (600, "Network Error: Request timed out")
    except requests.exceptions.RequestException as e:
        return (600, f"Network Error: {e}")
    except Exception as e:
        # Log unexpected errors for debugging
        print(f"Unexpected error in API call: {e}")
        print(traceback.format_exc())
        return (600, f"Unexpected Error: {e}")

class LeakCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Breached Email Checker")
        self.root.geometry("850x650")
        self.root.minsize(1500, 900)

        self.input_filepath = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready. Select a CSV file (username,password).")
        self.is_checking = False
        self.update_queue = Queue()

        style = ttk.Style()

        input_frame = ttk.Frame(root, padding="10")
        input_frame.pack(fill=X, side=TOP)
        ttk.Label(input_frame, text="Credentials File (.csv):").pack(side=LEFT, padx=(0, 5))
        self.file_entry = ttk.Entry(input_frame, textvariable=self.input_filepath, state=READONLY)
        self.file_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        self.browse_button = ttk.Button(input_frame, text="Browse...", command=self.browse_file, style='primary.TButton')
        self.browse_button.pack(side=LEFT, padx=(5, 0))

        action_frame = ttk.Frame(root, padding=(10, 0, 10, 10))
        action_frame.pack(fill=X, side=TOP)
        self.check_button = ttk.Button(action_frame, text="Check Emails", command=self.start_check_thread, style='success.TButton')
        self.check_button.pack(side=LEFT)

        results_frame = ttk.Frame(root, padding=(10, 0, 10, 0))
        results_frame.pack(fill=BOTH, expand=True)

        tree_columns = ("email", "status", "found", "sources")
        self.tree = ttk.Treeview(results_frame, columns=tree_columns, show="headings")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("status", text="Check Status")
        self.tree.heading("found", text="Found in Leaks?")
        self.tree.heading("sources", text="Details / Sources / Error")

        self.tree.column("email", width=250, anchor=W)
        self.tree.column("status", width=100, anchor=CENTER)
        self.tree.column("found", width=120, anchor=CENTER)
        self.tree.column("sources", width=300, anchor=W)

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.tree.tag_configure('found', background=style.colors.danger)
        self.tree.tag_configure('notfound', background=style.colors.success)
        self.tree.tag_configure('error', background=style.colors.warning)
        self.tree.tag_configure('skipped', foreground=style.colors.secondary)

        status_frame = ttk.Frame(root, padding=(10, 5, 10, 10))
        status_frame.pack(fill=X, side=BOTTOM)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_text, anchor=W)
        self.status_label.pack(side=LEFT, fill=X, expand=True)
        self.progress_bar = ttk.Progressbar(status_frame, mode='determinate', length=200)
        self.progress_bar.pack(side=RIGHT)

        self.root.after(100, self.process_queue)

    def browse_file(self):
        filepath = fd.askopenfilename(
            title="Select Credentials CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            self.input_filepath.set(filepath)
            self.status_text.set(f"Selected: {os.path.basename(filepath)}")

    def update_status(self, text):
        self.status_text.set(text)

    def add_result_to_tree(self, email, status, found_info, details):
        tag = ''
        if status == 'Checked':
            tag = 'found' if found_info == 'Yes' else 'notfound'
        elif status == 'Skipped':
            tag = 'skipped'
            found_info = 'N/A'
        else: # Error or other status
            tag = 'error'
            found_info = 'N/A'

        # Ensure details are string and truncate if excessively long for display
        details_str = str(details)
        if len(details_str) > 500:
             details_str = details_str[:497] + "..."

        try:
            self.tree.insert("", END, values=(email, status, found_info, details_str), tags=(tag,))
            self.tree.yview_moveto(1)
        except tk.TclError as e:
            print(f"Error adding to treeview: {e}. Data: {(email, status, found_info, details_str)}")
            # Attempt to insert with simplified data if specific error occurs (e.g., bad chars)
            try:
                 safe_details = ''.join(c for c in details_str if c.isprintable())
                 self.tree.insert("", END, values=(email, status, found_info, safe_details), tags=(tag,))
                 self.tree.yview_moveto(1)
            except Exception as inner_e:
                 print(f"Failed to add even simplified data to treeview: {inner_e}")


    def start_check_thread(self):
        filepath = self.input_filepath.get()
        if not filepath:
            msgbox.showwarning("No File Selected", "Please browse to select the credentials CSV file.")
            return
        if not os.path.exists(filepath):
            msgbox.showerror("File Not Found", f"The file '{filepath}' does not exist.")
            return
        if self.is_checking:
            msgbox.showwarning("Already Running", "A check is already in progress.")
            return

        self.is_checking = True
        self.check_button.config(state=DISABLED)
        self.browse_button.config(state=DISABLED)
        self.status_text.set("Starting check...")
        self.progress_bar['value'] = 0
        # Clear previous results safely
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
        except tk.TclError as e:
             print(f"Error clearing treeview: {e}") # Log error but continue

        self.check_thread = threading.Thread(target=self.perform_check, args=(filepath,), daemon=True)
        self.check_thread.start()

    def perform_check(self, filepath):
        emails_to_check = []
        invalid_emails = []
        try:
            with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f: # Ignore encoding errors
                reader = csv.reader(f)
                try:
                    header = next(reader)
                    if not header or not header[0] or header[0].strip().lower() != 'username':
                        print("CSV header 'username' not found, invalid, or missing. Assuming first column is username/email.")
                        # Attempt to rewind if header was actually data (simple case)
                        try:
                            f.seek(0)
                            reader = csv.reader(f) # Recreate reader
                        except Exception:
                            pass # If seek fails, just proceed assuming header was skipped
                except StopIteration:
                    self.update_queue.put(("update_status", "Error: CSV file is empty."))
                    self.update_queue.put(("check_complete", None))
                    return
                except csv.Error as e:
                    self.update_queue.put(("error_message", ("CSV Read Error", f"Error reading CSV header/first line: {e}")))
                    self.update_queue.put(("check_complete", None))
                    return

                line_num = 1
                for row in reader:
                    line_num += 1
                    if row and row[0]: # Ensure row and first element exist
                        potential_email = row[0].strip()
                        if re.match(EMAIL_REGEX, potential_email):
                            emails_to_check.append(potential_email)
                        else:
                            invalid_emails.append(potential_email)
                            self.update_queue.put(("add_result", (potential_email, "Skipped", "N/A", "Invalid email format")))
                    else:
                        print(f"Skipping empty or invalid row at line {line_num}")

            total_valid_emails = len(emails_to_check)
            skipped_count = len(invalid_emails)

            if total_valid_emails == 0:
                status_msg = "No valid emails found in the first column."
                if skipped_count > 0:
                    status_msg += f" Skipped {skipped_count} invalid entries."
                self.update_queue.put(("update_status", status_msg))
                self.update_queue.put(("check_complete", None))
                return

            self.update_queue.put(("set_progress_max", total_valid_emails))
            status_msg = f"Found {total_valid_emails} valid emails to check."
            if skipped_count > 0:
                status_msg += f" Skipped {skipped_count} invalid."
            self.update_queue.put(("update_status", status_msg))


            checked_count = 0
            while checked_count < total_valid_emails:
                # Check if root window still exists before proceeding
                if not self.root.winfo_exists():
                    print("Main window closed, stopping check thread.")
                    break

                email = emails_to_check[checked_count]
                self.update_queue.put(("update_status", f"Checking {checked_count+1}/{total_valid_emails}: {email}"))

                status_code, result = check_email_leak_api(email)

                if status_code == 200:
                    found = result.get('found', False)
                    sources_data = result.get('sources', [])
                    details = f"{len(sources_data)} sources" if found else "Not found"

                    if found and sources_data:
                        # --- FIX IMPLEMENTED HERE ---
                        source_names = []
                        for source in sources_data[:5]: # Iterate through first 5
                             if isinstance(source, dict):
                                 # Prioritize 'title', then 'name', then default
                                 name = source.get('title', source.get('name', 'Unknown Source'))
                                 source_names.append(str(name))
                             elif isinstance(source, str):
                                 source_names.append(source) # Handle if it's already a string
                             else:
                                 source_names.append('Invalid Source Data') # Handle other types

                        details += f": {', '.join(source_names)}"
                        # --- END FIX ---
                        if len(sources_data) > 5:
                            details += "..."

                    self.update_queue.put(("add_result", (email, "Checked", "Yes" if found else "No", details)))
                    checked_count += 1
                    self.update_queue.put(("update_progress", checked_count))
                    time.sleep(REQUEST_DELAY_SECONDS)

                elif status_code == 429: # Rate Limited
                    wait_time = result
                    self.update_queue.put(("update_status", f"Rate limited checking {email}. Waiting {wait_time}s..."))
                    # Check window existence before sleeping
                    if self.root.winfo_exists():
                        time.sleep(wait_time)
                    else:
                        print("Main window closed during rate limit wait, stopping.")
                        break # Exit loop if window closed
                    # Loop will retry the *same* email

                else: # API Error or Network Error
                    self.update_queue.put(("add_result", (email, f"Error ({status_code})", "N/A", str(result))))
                    checked_count += 1 # Move to next email even on error
                    self.update_queue.put(("update_progress", checked_count))
                    time.sleep(REQUEST_DELAY_SECONDS) # Still delay after error

        except FileNotFoundError:
             self.update_queue.put(("error_message", ("File Not Found", f"The file '{filepath}' was not found.")))
        except PermissionError:
             self.update_queue.put(("error_message", ("Permission Error", f"Could not read the file '{filepath}'. Check permissions.")))
        except csv.Error as e:
             self.update_queue.put(("error_message", ("CSV Error", f"Error processing CSV file: {e}")))
        except Exception as e:
            # Log the full traceback to console for debugging
            print("--- Unhandled Exception in perform_check ---")
            print(traceback.format_exc())
            print("--------------------------------------------")
            self.update_queue.put(("error_message", ("General Error", f"An unexpected error occurred: {e}")))
        finally:
            # Ensure check_complete is always sent unless window closed
            if self.root.winfo_exists():
                 self.update_queue.put(("check_complete", None))
            else:
                 print("Check thread finished after window closed.")


    def process_queue(self):
        try:
            while True:
                # Check if the window is destroyed before processing queue
                if not self.root.winfo_exists():
                    return # Stop processing if window is gone

                task, args = self.update_queue.get_nowait()

                if task == "update_status":
                    self.update_status(args)
                elif task == "add_result":
                    self.add_result_to_tree(*args)
                elif task == "update_progress":
                    # Ensure progress bar max is set before updating value
                    if self.progress_bar['maximum'] > 0:
                        self.progress_bar['value'] = args
                elif task == "set_progress_max":
                    self.progress_bar['maximum'] = args if args > 0 else 1 # Avoid max=0
                    self.progress_bar['value'] = 0 # Reset value when max changes
                elif task == "check_complete":
                    self.check_button.config(state=NORMAL)
                    self.browse_button.config(state=NORMAL)
                    self.is_checking = False
                    # Keep final count in status if progress occurred
                    final_max = self.progress_bar['maximum']
                    if final_max > 1: # Check if progress was actually set
                         self.update_status(f"Check complete! Processed {final_max} valid emails.")
                    else:
                         self.update_status("Check complete!") # Default message
                    self.progress_bar['value'] = 0
                    # No break here, let the after() call handle rescheduling
                elif task == "error_message":
                    # Check window existence again before showing messagebox
                    if self.root.winfo_exists():
                        msgbox.showerror(args[0], args[1])
                    else:
                        print(f"Window closed. Suppressed error message: {args[0]} - {args[1]}")


        except Empty: # Correct exception name
            pass # Queue is empty, do nothing this cycle
        except Exception as e:
            # Catch potential errors during queue processing itself
            print(f"Error processing GUI update queue: {e}")
            print(traceback.format_exc())
        finally:
            # Always reschedule the check if the window still exists
            if self.root.winfo_exists():
                self.root.after(100, self.process_queue)


if __name__ == "__main__":
    # Handle potential display issues on some systems
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Could not set DPI awareness: {e}")

    root = ttk.Window(themename="superhero")
    app = LeakCheckerApp(root)
    root.mainloop()
