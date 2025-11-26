import tkinter as tk
from tkinter import ttk
import subprocess
import os
import sys
from pathlib import Path

# Repo root - this file lives in <repo>/main/
BASE_DIR = Path(__file__).resolve().parent.parent

class ForensiQLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("ForensiQ Project Launcher")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        # Set background color
        self.root.configure(bg="#f5f6fa")

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', background="#f5f6fa")
        style.configure('Status.TLabel', background="#f5f6fa")

        # Main frame with padding
        main_frame = tk.Frame(root, bg="#f5f6fa", padx=40, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title with better styling
        title_label = tk.Label(
            main_frame,
            text="ForensiQ Project Launcher",
            font=("Segoe UI", 24, "bold"),
            fg="#2c3e50",
            bg="#f5f6fa"
        )
        title_label.pack(pady=(0, 10))

        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Select a project to launch",
            font=("Segoe UI", 11),
            fg="#7f8c8d",
            bg="#f5f6fa"
        )
        subtitle_label.pack(pady=(0, 40))

        # Button frame
        button_frame = tk.Frame(main_frame, bg="#f5f6fa")
        button_frame.pack(fill=tk.BOTH, expand=True)

        # Project paths, resolved from the repo root so this works on any
        # machine. Each project lists candidates in order of preference - the
        # network exe only exists once build.bat has been run, so fall back to
        # launching the GUI script directly.
        self.projects = {
            "ForensiQ Network": [
                (BASE_DIR / "ForensiQ_network" / "code" / "dist" / "ForensiQ.exe", "exe"),
                (BASE_DIR / "ForensiQ_network" / "code" / "run_gui.py", "python"),
            ],
            "ForensiQ Android": [
                (BASE_DIR / "ForensiQ_android" / "gui.py", "python"),
            ],
            "ForensiQ Windows": [
                (BASE_DIR / "ForensiQ_windows" / "run.py", "python"),
            ]
        }

        # Create buttons with icons and better styling
        button_configs = [
            ("ForensiQ Network", "#3498db", "🌐"),
            ("ForensiQ Android", "#2ecc71", "📱"),
            ("ForensiQ Windows", "#e74c3c", "🪟")
        ]

        for project_name, color, icon in button_configs:
            # Button container for shadow effect
            btn_container = tk.Frame(button_frame, bg="#f5f6fa")
            btn_container.pack(pady=15, fill=tk.X)

            btn = tk.Button(
                btn_container,
                text=f"{icon}  {project_name}",
                font=("Segoe UI", 14, "bold"),
                bg=color,
                fg="white",
                activebackground=self._darken_color(color),
                activeforeground="white",
                relief=tk.FLAT,
                bd=0,
                padx=40,
                pady=20,
                cursor="hand2",
                command=lambda name=project_name: self.launch_project(name),
                highlightthickness=0,
                width=30,
                height=2
            )
            btn.pack(fill=tk.X)

            # Add hover effect binding
            btn.bind("<Enter>", lambda e, c=color: self._on_enter(e, c))
            btn.bind("<Leave>", lambda e, c=color: self._on_leave(e, c))

        # Status label with better styling
        status_frame = tk.Frame(main_frame, bg="#f5f6fa")
        status_frame.pack(pady=(30, 0))

        self.status_label = tk.Label(
            status_frame,
            text="Ready to launch",
            font=("Segoe UI", 10),
            fg="#7f8c8d",
            bg="#f5f6fa"
        )
        self.status_label.pack()

    def _on_enter(self, event, color):
        """Button hover effect"""
        event.widget.config(bg=self._darken_color(color))

    def _on_leave(self, event, color):
        """Button leave effect"""
        event.widget.config(bg=color)

    def _darken_color(self, color):
        """Darken a hex color for hover effect"""
        color_map = {
            "#3498db": "#2980b9",
            "#2ecc71": "#27ae60",
            "#e74c3c": "#c0392b"
        }
        return color_map.get(color, color)

    def launch_project(self, project_name):
        """Launch the selected project"""
        candidates = self.projects.get(project_name)
        if not candidates:
            self.update_status(f"Error: Project '{project_name}' not found", "error")
            return

        # Use the first candidate that actually exists on this machine
        for candidate, project_type in candidates:
            if candidate.exists():
                path = str(candidate)
                break
        else:
            self.update_status(f"Error: {project_name} not found under {BASE_DIR}", "error")
            return

        try:
            # Run from the project's own folder - these scripts look for
            # their .ps1 files and templates by relative name
            workdir = os.path.dirname(path)
            if project_type == "exe":
                # Launch executable
                subprocess.Popen([path], shell=True, cwd=workdir)
            elif project_type == "python":
                # Launch Python script
                subprocess.Popen([sys.executable, path], shell=True, cwd=workdir)
            elif project_type == "batch":
                # Launch batch file - use cmd.exe /c for proper execution
                subprocess.Popen(['cmd.exe', '/c', path], shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)

            self.update_status(f"Launched: {project_name}", "success")
        except Exception as e:
            self.update_status(f"Error launching {project_name}: {str(e)}", "error")

    def update_status(self, message, status_type="info"):
        """Update status label"""
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "info": "#7f8c8d"
        }
        self.status_label.config(text=message, fg=colors.get(status_type, "#7f8c8d"))

def main():
    root = tk.Tk()
    app = ForensiQLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()

