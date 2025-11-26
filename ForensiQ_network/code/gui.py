

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from datetime import datetime
import json

COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_medium': '#16213e',
    'bg_light': '#0f3460',
    'bg_panel': '#1e293b',
    'accent': '#0ea5e9',
    'accent_dark': '#0284c7',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'text_primary': '#ffffff',
    'text_secondary': '#cbd5e1',
    'text_muted': '#94a3b8',
    'border': '#334155',
    'card_bg': '#1e293b',
    'hover': '#2d3748',
}

from forensics import (
    PacketCapture, ProtocolAnalyzer, FlowAnalyzer,
    IntrusionDetector, NetworkVisualizer, ReportGenerator
)
from scapy.all import get_if_list


class NetworkForensicsGUI:
    
    
    def __init__(self, root):
        self.root = root
        self.root.title("ForensiQ (Network) - Network Security Analysis")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        self.root.configure(bg=COLORS['bg_dark'])
        
        self.root.option_add('*Text*background', COLORS['bg_medium'])
        self.root.option_add('*Text*foreground', COLORS['text_primary'])
        self.root.option_add('*Text*selectBackground', COLORS['accent'])
        self.root.option_add('*Text*selectForeground', COLORS['text_primary'])
        self.root.option_add('*Text*insertBackground', COLORS['text_primary'])
        
        self.developers = (
            "Developers: Manish Kumar, Anshul Gadia, Tanish Dhingra, Mukul Dev"
        )

        self.capture_instance = None
        self.capture_thread = None
        self.current_pcap_file = None
        self.analysis_results = {}
        
        self.setup_styles()
        
        self.create_header()
        self.create_widgets()
        self.create_status_bar()
        
        self.center_window()
    
    def setup_styles(self):
        
        style = ttk.Style()
        style.theme_use('clam')
        
        font_primary = ('Segoe UI', 10)
        font_bold = ('Segoe UI', 10, 'bold')
        font_title = ('Segoe UI', 20, 'bold')
        font_heading = ('Segoe UI', 12, 'bold')
        font_status = ('Segoe UI', 9)
        
        style.configure('Title.TLabel', 
                       font=font_title,
                       background=COLORS['bg_dark'],
                       foreground=COLORS['text_primary'])
        
        style.configure('Heading.TLabel',
                       font=font_heading,
                       background=COLORS['card_bg'],
                       foreground=COLORS['text_primary'])
        
        style.configure('Status.TLabel',
                       font=font_status,
                       background=COLORS['bg_medium'],
                       foreground=COLORS['text_secondary'])
        
        style.configure('Modern.TButton',
                       font=font_bold,
                       background=COLORS['accent'],
                       foreground=COLORS['text_primary'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        style.map('Modern.TButton',
                 background=[('active', COLORS['accent_dark']),
                            ('pressed', COLORS['accent_dark'])])
        
        style.configure('Success.TButton',
                       font=font_bold,
                       background=COLORS['success'],
                       foreground=COLORS['text_primary'],
                       borderwidth=0,
                       padding=(20, 10))
        
        style.map('Success.TButton',
                 background=[('active', '
                            ('pressed', '
        
        style.configure('Danger.TButton',
                       font=font_bold,
                       background=COLORS['danger'],
                       foreground=COLORS['text_primary'],
                       borderwidth=0,
                       padding=(20, 10))
        
        style.map('Danger.TButton',
                 background=[('active', '
                            ('pressed', '
        
        style.configure('TNotebook',
                       background=COLORS['bg_dark'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab',
                       font=font_bold,
                       background=COLORS['bg_light'],
                       foreground=COLORS['text_secondary'],
                       padding=(20, 12),
                       borderwidth=0)
        
        style.map('TNotebook.Tab',
                 background=[('selected', COLORS['accent'])],
                 foreground=[('selected', COLORS['text_primary'])],
                 expand=[('selected', [1, 1, 1, 0])])
        
        style.configure('TLabelframe',
                       background=COLORS['card_bg'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat')
        
        style.configure('TLabelframe.Label',
                       font=font_heading,
                       background=COLORS['card_bg'],
                       foreground=COLORS['accent'])
        
        style.configure('Card.TFrame',
                       background=COLORS['card_bg'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Modern.TEntry',
                       font=font_primary,
                       fieldbackground=COLORS['bg_medium'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       padding=5)
        
        style.configure('Modern.TCombobox',
                       font=font_primary,
                       fieldbackground=COLORS['bg_medium'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       padding=5)
        
        style.configure('Modern.Vertical.TScrollbar',
                       background=COLORS['bg_medium'],
                       troughcolor=COLORS['bg_dark'],
                       borderwidth=0,
                       arrowcolor=COLORS['text_secondary'],
                       darkcolor=COLORS['bg_medium'],
                       lightcolor=COLORS['bg_medium'])
        
        style.configure('Modern.TCheckbutton',
                       font=font_primary,
                       background=COLORS['card_bg'],
                       foreground=COLORS['text_primary'],
                       focuscolor='none')
        
        style.configure('Modern.Treeview',
                       font=font_primary,
                       background=COLORS['bg_medium'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['bg_medium'],
                       borderwidth=0)
        
        style.configure('Modern.Treeview.Heading',
                       font=font_bold,
                       background=COLORS['accent'],
                       foreground=COLORS['text_primary'],
                       borderwidth=0)
        
        style.map('Modern.Treeview',
                 background=[('selected', COLORS['accent'])],
                 foreground=[('selected', COLORS['text_primary'])])
    
    def center_window(self):
        
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        
        header_frame = tk.Frame(self.root, bg=COLORS['bg_medium'], height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg=COLORS['bg_medium'])
        title_frame.pack(side=tk.LEFT, padx=30, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="ForensiQ",
            font=('Segoe UI', 28, 'bold'),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary']
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Network Forensics & Security Analysis",
            font=('Segoe UI', 11),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_secondary']
        )
        subtitle_label.pack(anchor=tk.W)
        
        accent_line = tk.Frame(header_frame, bg=COLORS['accent'], height=4)
        accent_line.pack(fill=tk.X, side=tk.BOTTOM)
    
    def create_widgets(self):
        
        main_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notebook = ttk.Notebook(main_container, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_capture_tab()
        self.create_analysis_tab()
        self.create_flows_tab()
        self.create_detection_tab()
        self.create_visualization_tab()
        self.create_reports_tab()
    
    def create_status_bar(self):
        
        self.status_frame = tk.Frame(self.root, bg=COLORS['bg_medium'], height=35)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)
        
        left_section = tk.Frame(self.status_frame, bg=COLORS['bg_medium'])
        left_section.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.status_label = tk.Label(
            left_section,
            text="● Ready",
            font=('Segoe UI', 9),
            bg=COLORS['bg_medium'],
            fg=COLORS['success'],
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT)
        
        middle_section = tk.Frame(self.status_frame, bg=COLORS['bg_medium'])
        middle_section.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=20, pady=5)
        
        self.developers_label = tk.Label(
            middle_section,
            text=self.developers,
            font=('Segoe UI', 8),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_muted'],
            anchor='w'
        )
        self.developers_label.pack(side=tk.LEFT)

        right_section = tk.Frame(self.status_frame, bg=COLORS['bg_medium'])
        right_section.pack(side=tk.RIGHT, padx=15, pady=5)
        
        self.time_label = tk.Label(
            right_section,
            text="",
            font=('Segoe UI', 9),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_secondary']
        )
        self.time_label.pack(side=tk.RIGHT)
        self.update_time()
        
        border_line = tk.Frame(self.status_frame, bg=COLORS['border'], height=1)
        border_line.pack(fill=tk.X, side=tk.TOP)
    
    def update_time(self):
        
        if hasattr(self, 'time_label') and self.time_label:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
                                                   
        if hasattr(self, 'time_label'):
            self.root.after(1000, self.update_time)
    
    def update_status(self, message, status_type='info'):
        
        if hasattr(self, 'status_label') and self.status_label:
            status_colors = {
                'info': COLORS['accent'],
                'success': COLORS['success'],
                'warning': COLORS['warning'],
                'error': COLORS['danger'],
                'ready': COLORS['success']
            }
            color = status_colors.get(status_type, COLORS['text_secondary'])
            self.status_label.config(text=f"● {message}", fg=color)
            self.root.update_idletasks()
    
                                              
    
    def create_capture_tab(self):
        
        capture_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(capture_frame, text="📡 Capture")
        
        title_frame = tk.Frame(capture_frame, bg=COLORS['bg_dark'])
        title_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        title = tk.Label(
            title_frame,
            text="Live Packet Capture",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            title_frame,
            text="Capture network traffic in real-time from your network interfaces",
            font=('Segoe UI', 10),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_muted'],
            anchor='w'
        )
        subtitle.pack(anchor=tk.W, pady=(5, 0))
        
        settings_card = tk.Frame(capture_frame, bg=COLORS['card_bg'], relief='flat')
        settings_card.pack(fill=tk.X, padx=20, pady=10)
        
        settings_title = tk.Label(
            settings_card,
            text="Capture Settings",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['accent'],
            anchor='w'
        )
        settings_title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        settings_frame = tk.Frame(settings_card, bg=COLORS['card_bg'])
        settings_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        interface_label = tk.Label(
            settings_frame,
            text="Network Interface:",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        interface_label.grid(row=0, column=0, sticky=tk.W, pady=8)
        
        self.interface_var = tk.StringVar()
        interface_container = tk.Frame(settings_frame, bg=COLORS['card_bg'])
        interface_container.grid(row=0, column=1, padx=(10, 5), pady=8, sticky=tk.EW)
        
        self.interface_combo = ttk.Combobox(
            interface_container,
            textvariable=self.interface_var,
            width=35,
            style='Modern.TCombobox'
        )
        self.interface_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        refresh_btn = ttk.Button(
            interface_container,
            text="🔄 Refresh",
            command=self.refresh_interfaces,
            style='Modern.TButton'
        )
        refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        output_label = tk.Label(
            settings_frame,
            text="Output File:",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        output_label.grid(row=1, column=0, sticky=tk.W, pady=8)
        
        self.output_file_var = tk.StringVar(value="capture.pcap")
        output_container = tk.Frame(settings_frame, bg=COLORS['card_bg'])
        output_container.grid(row=1, column=1, padx=(10, 5), pady=8, sticky=tk.EW)
        
        output_entry = ttk.Entry(
            output_container,
            textvariable=self.output_file_var,
            width=35,
            style='Modern.TEntry'
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(
            output_container,
            text="📁 Browse",
            command=self.browse_output_file,
            style='Modern.TButton'
        )
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        filter_label = tk.Label(
            settings_frame,
            text="BPF Filter:",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        filter_label.grid(row=2, column=0, sticky=tk.W, pady=8)
        
        self.filter_var = tk.StringVar()
        filter_container = tk.Frame(settings_frame, bg=COLORS['card_bg'])
        filter_container.grid(row=2, column=1, padx=(10, 5), pady=8, sticky=tk.EW)
        
        filter_entry = ttk.Entry(
            filter_container,
            textvariable=self.filter_var,
            width=35,
            style='Modern.TEntry'
        )
        filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        filter_hint = tk.Label(
            filter_container,
            text="(e.g., tcp port 80)",
            font=('Segoe UI', 8),
            bg=COLORS['card_bg'],
            fg=COLORS['text_muted']
        )
        filter_hint.pack(side=tk.LEFT, padx=(10, 0))
        
        settings_frame.columnconfigure(1, weight=1)
        
        options_card = tk.Frame(capture_frame, bg=COLORS['card_bg'], relief='flat')
        options_card.pack(fill=tk.X, padx=20, pady=10)
        
        options_title = tk.Label(
            options_card,
            text="Capture Options",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['accent'],
            anchor='w'
        )
        options_title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        options_frame = tk.Frame(options_card, bg=COLORS['card_bg'])
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        count_label = tk.Label(
            options_frame,
            text="Packet Count:",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        count_label.grid(row=0, column=0, sticky=tk.W, pady=8)
        
        self.count_var = tk.StringVar(value="0")
        count_container = tk.Frame(options_frame, bg=COLORS['card_bg'])
        count_container.grid(row=0, column=1, padx=(10, 5), pady=8, sticky=tk.W)
        
        count_entry = ttk.Entry(
            count_container,
            textvariable=self.count_var,
            width=20,
            style='Modern.TEntry'
        )
        count_entry.pack(side=tk.LEFT)
        
        count_hint = tk.Label(
            count_container,
            text="(0 = unlimited)",
            font=('Segoe UI', 8),
            bg=COLORS['card_bg'],
            fg=COLORS['text_muted']
        )
        count_hint.pack(side=tk.LEFT, padx=(10, 0))
        
        duration_label = tk.Label(
            options_frame,
            text="Duration (seconds):",
            font=('Segoe UI', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w'
        )
        duration_label.grid(row=1, column=0, sticky=tk.W, pady=8)
        
        self.duration_var = tk.StringVar(value="")
        duration_container = tk.Frame(options_frame, bg=COLORS['card_bg'])
        duration_container.grid(row=1, column=1, padx=(10, 5), pady=8, sticky=tk.W)
        
        duration_entry = ttk.Entry(
            duration_container,
            textvariable=self.duration_var,
            width=20,
            style='Modern.TEntry'
        )
        duration_entry.pack(side=tk.LEFT)
        
        duration_hint = tk.Label(
            duration_container,
            text="(empty = unlimited)",
            font=('Segoe UI', 8),
            bg=COLORS['card_bg'],
            fg=COLORS['text_muted']
        )
        duration_hint.pack(side=tk.LEFT, padx=(10, 0))
        
        control_frame = tk.Frame(capture_frame, bg=COLORS['bg_dark'])
        control_frame.pack(pady=15)
        
        self.start_capture_btn = ttk.Button(
            control_frame,
            text="▶ Start Capture",
            command=self.start_capture,
            style='Success.TButton'
        )
        self.start_capture_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_capture_btn = ttk.Button(
            control_frame,
            text="⏹ Stop Capture",
            command=self.stop_capture,
            style='Danger.TButton',
            state=tk.DISABLED
        )
        self.stop_capture_btn.pack(side=tk.LEFT, padx=10)
        
        stats_card = tk.Frame(capture_frame, bg=COLORS['card_bg'], relief='flat')
        stats_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        stats_title = tk.Label(
            stats_card,
            text="Capture Statistics",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['accent'],
            anchor='w'
        )
        stats_title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        stats_frame = tk.Frame(stats_card, bg=COLORS['card_bg'])
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        text_frame = tk.Frame(stats_frame, bg=COLORS['bg_medium'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = scrolledtext.ScrolledText(
            text_frame,
            height=10,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text_primary'],
            borderwidth=0,
            relief='flat',
            padx=10,
            pady=10
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
                                    
        self.refresh_interfaces()
    
    def refresh_interfaces(self):
        
        try:
            interfaces = get_if_list()
            self.interface_combo['values'] = interfaces
            if interfaces:
                                                     
                active = PacketCapture.get_active_interface()
                if active and active in interfaces:
                    self.interface_var.set(active)
                else:
                    self.interface_var.set(interfaces[0])
            self.update_status("Interfaces refreshed", 'success')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh interfaces: {e}")
    
    def browse_output_file(self):
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pcap",
            filetypes=[("PCAP files", "*.pcap"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
    
    def start_capture(self):
        
        interface = self.interface_var.get()
        if not interface:
            messagebox.showerror("Error", "Please select a network interface")
            return
        
        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file")
            return
        
        try:
            count = int(self.count_var.get()) if self.count_var.get() else 0
            duration = int(self.duration_var.get()) if self.duration_var.get() else None
            filter_str = self.filter_var.get() if self.filter_var.get() else None
            
            self.capture_instance = PacketCapture(
                interface=interface,
                output_file=output_file,
                filter=filter_str,
                count=count
            )
            
                                     
            self.capture_thread = threading.Thread(
                target=self._run_capture,
                args=(duration,),
                daemon=True
            )
            self.capture_thread.start()
            
                       
            self.start_capture_btn.config(state=tk.DISABLED)
            self.stop_capture_btn.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"Capture started on {interface}\n")
            self.stats_text.insert(tk.END, f"Output: {output_file}\n")
            if filter_str:
                self.stats_text.insert(tk.END, f"Filter: {filter_str}\n")
            self.stats_text.insert(tk.END, "-" * 50 + "\n")
            
            self.update_status(f"Capturing on {interface}...", 'info')
            
                                     
            self.update_capture_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start capture: {e}")
    
    def _run_capture(self, duration):
        
        try:
            self.capture_instance.start(duration=duration)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Capture Error", str(e)))
    
    def stop_capture(self):
        
        if self.capture_instance and self.capture_instance.is_capturing:
            self.capture_instance.stop()
            self.update_status("Capture stopped", 'info')
        
                   
        self.start_capture_btn.config(state=tk.NORMAL)
        self.stop_capture_btn.config(state=tk.DISABLED)
        
                          
        if self.capture_instance:
            stats = self.capture_instance.get_statistics()
            self.stats_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            self.stats_text.insert(tk.END, "Capture Complete!\n")
            self.stats_text.insert(tk.END, f"Total Packets: {stats.get('total_packets', 0)}\n")
            self.stats_text.insert(tk.END, f"Total Bytes: {stats.get('total_bytes', 0):,}\n")
            if 'duration' in stats:
                self.stats_text.insert(tk.END, f"Duration: {stats['duration']:.2f} seconds\n")
    
    def update_capture_stats(self):
        
        if self.capture_instance and self.capture_instance.is_capturing:
            stats = self.capture_instance.get_statistics()
            packet_count = stats.get('total_packets', 0)
            
                                  
            self.stats_text.insert(tk.END, f"Packets captured: {packet_count}\n")
            self.stats_text.see(tk.END)
            
                                  
            self.root.after(1000, self.update_capture_stats)
        elif self.capture_instance and not self.capture_instance.is_capturing:
                                         
            self.root.after(0, self.stop_capture)
    
                                        
    
    def create_analysis_tab(self):
        
        analysis_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(analysis_frame, text="📊 Analysis")
        
        title_frame = tk.Frame(analysis_frame, bg=COLORS['bg_dark'])
        title_frame.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        title = tk.Label(
            title_frame,
            text="PCAP File Analysis",
            font=('Segoe UI', 18, 'bold'),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_primary'],
            anchor='w'
        )
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            title_frame,
            text="Analyze captured network traffic files for protocols, flows, and security threats",
            font=('Segoe UI', 10),
            bg=COLORS['bg_dark'],
            fg=COLORS['text_muted'],
            anchor='w'
        )
        subtitle.pack(anchor=tk.W, pady=(5, 0))
        
        file_card = tk.Frame(analysis_frame, bg=COLORS['card_bg'], relief='flat')
        file_card.pack(fill=tk.X, padx=20, pady=10)
        
        file_title = tk.Label(
            file_card,
            text="File Selection",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['accent'],
            anchor='w'
        )
        file_title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        file_frame = tk.Frame(file_card, bg=COLORS['card_bg'])
        file_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.pcap_file_var = tk.StringVar()
        file_entry = ttk.Entry(
            file_frame,
            textvariable=self.pcap_file_var,
            width=50,
            style='Modern.TEntry'
        )
        file_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(
            file_frame,
            text="📁 Browse",
            command=self.browse_pcap_file,
            style='Modern.TButton'
        )
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_btn = ttk.Button(
            file_frame,
            text="▶ Analyze",
            command=self.analyze_pcap,
            style='Success.TButton'
        )
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        options_card = tk.Frame(analysis_frame, bg=COLORS['card_bg'], relief='flat')
        options_card.pack(fill=tk.X, padx=20, pady=10)
        
        options_title = tk.Label(
            options_card,
            text="Analysis Options",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['accent'],
            anchor='w'
        )
        options_title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        options_frame = tk.Frame(options_card, bg=COLORS['card_bg'])
        options_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.analyze_protocols_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Protocol Analysis",
            variable=self.analyze_protocols_var,
            style='Modern.TCheckbutton'
        ).pack(side=tk.LEFT, padx=15)
        
        self.analyze_flows_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Flow Analysis",
            variable=self.analyze_flows_var,
            style='Modern.TCheckbutton'
        ).pack(side=tk.LEFT, padx=15)
        
        self.analyze_intrusion_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Intrusion Detection",
            variable=self.analyze_intrusion_var,
            style='Modern.TCheckbutton'
        ).pack(side=tk.LEFT, padx=15)
        
        results_card = tk.Frame(analysis_frame, bg=COLORS['card_bg'], relief='flat')
        results_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        results_title = tk.Label(
            results_card,
            text="Analysis Results",
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['accent'],
            anchor='w'
        )
        results_title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        results_frame = tk.Frame(results_card, bg=COLORS['card_bg'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.results_notebook = ttk.Notebook(results_frame, style='TNotebook')
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        summary_frame = tk.Frame(self.results_notebook, bg=COLORS['bg_medium'])
        self.summary_text = scrolledtext.ScrolledText(
            summary_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text_primary'],
            borderwidth=0,
            relief='flat',
            padx=10,
            pady=10
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        self.results_notebook.add(summary_frame, text="Summary")
        
        protocol_frame = tk.Frame(self.results_notebook, bg=COLORS['bg_medium'])
        self.protocol_text = scrolledtext.ScrolledText(
            protocol_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text_primary'],
            borderwidth=0,
            relief='flat',
            padx=10,
            pady=10
        )
        self.protocol_text.pack(fill=tk.BOTH, expand=True)
        self.results_notebook.add(protocol_frame, text="Protocol Details")
        
        http_frame = tk.Frame(self.results_notebook, bg=COLORS['bg_medium'])
        self.http_text = scrolledtext.ScrolledText(
            http_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text_primary'],
            borderwidth=0,
            relief='flat',
            padx=10,
            pady=10
        )
        self.http_text.pack(fill=tk.BOTH, expand=True)
        self.results_notebook.add(http_frame, text="HTTP Traffic")
        
        dns_frame = tk.Frame(self.results_notebook, bg=COLORS['bg_medium'])
        self.dns_text = scrolledtext.ScrolledText(
            dns_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg=COLORS['bg_medium'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text_primary'],
            borderwidth=0,
            relief='flat',
            padx=10,
            pady=10
        )
        self.dns_text.pack(fill=tk.BOTH, expand=True)
        self.results_notebook.add(dns_frame, text="DNS Traffic")
    
    def browse_pcap_file(self):
        
        filename = filedialog.askopenfilename(
            filetypes=[("PCAP files", "*.pcap *.pcapng"), ("All files", "*.*")]
        )
        if filename:
            self.pcap_file_var.set(filename)
            self.current_pcap_file = filename
    
    def analyze_pcap(self):
        
        pcap_file = self.pcap_file_var.get()
        if not pcap_file or not os.path.exists(pcap_file):
            messagebox.showerror("Error", "Please select a valid PCAP file")
            return
        
        self.current_pcap_file = pcap_file
        
                                
        self.summary_text.delete(1.0, tk.END)
        self.protocol_text.delete(1.0, tk.END)
        self.http_text.delete(1.0, tk.END)
        self.dns_text.delete(1.0, tk.END)
        
        self.update_status("Analyzing PCAP file...", 'info')
        
                                
        thread = threading.Thread(target=self._run_analysis, daemon=True)
        thread.start()
    
    def _run_analysis(self):
        
        try:
            pcap_file = self.current_pcap_file
            results = {}
            
                               
            if self.analyze_protocols_var.get():
                self.root.after(0, lambda: self.update_status("Running protocol analysis...", 'info'))
                analyzer = ProtocolAnalyzer(pcap_file)
                analysis_results = analyzer.analyze()
                results['protocol'] = analysis_results
                results['analyzer'] = analyzer
                
                                          
                self.root.after(0, lambda: self._display_protocol_results(analysis_results))
            
                           
            if self.analyze_flows_var.get():
                self.root.after(0, lambda: self.update_status("Extracting network flows...", 'info'))
                flow_analyzer = FlowAnalyzer(pcap_file)
                flows = flow_analyzer.extract_flows()
                flow_stats = flow_analyzer.get_flow_statistics()
                results['flows'] = flows
                results['flow_stats'] = flow_stats
                results['flow_analyzer'] = flow_analyzer
            
                                 
            if self.analyze_intrusion_var.get():
                self.root.after(0, lambda: self.update_status("Running intrusion detection...", 'info'))
                detector = IntrusionDetector(pcap_file)
                threats = detector.detect_anomalies()
                threat_summary = detector.get_threat_summary()
                results['threats'] = threats
                results['threat_summary'] = threat_summary
                results['detector'] = detector
            
            self.analysis_results = results
            
                             
            self.root.after(0, lambda: self._display_summary(results))
            
            self.root.after(0, lambda: self.update_status("Analysis complete", 'success'))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", str(e)))
            self.root.after(0, lambda: self.update_status("Analysis failed", 'error'))
    
    def _display_summary(self, results):
        
        summary = []
        summary.append("=" * 60)
        summary.append("ANALYSIS SUMMARY")
        summary.append("=" * 60)
        summary.append("")
        
        if 'analyzer' in results:
            analyzer = results['analyzer']
            summary.append(f"Total Packets: {len(analyzer.packets)}")
            summary.append("")
        
        if 'flow_stats' in results:
            stats = results['flow_stats']
            summary.append("Flow Statistics:")
            summary.append(f"  Total Flows: {stats.get('total_flows', 0)}")
            summary.append(f"  Total Packets: {stats.get('total_packets', 0)}")
            summary.append(f"  Total Bytes: {stats.get('total_bytes', 0):,}")
            summary.append("")
        
        if 'threat_summary' in results:
            threat_summary = results['threat_summary']
            summary.append("Security Analysis:")
            summary.append(f"  Threats Detected: {threat_summary.get('total_threats', 0)}")
            summary.append(f"  Anomalies Detected: {threat_summary.get('total_anomalies', 0)}")
            summary.append(f"  Unique Source IPs: {threat_summary.get('unique_source_ips', 0)}")
            summary.append("")
        
        if 'protocol' in results:
            protocol_results = results['protocol']
            if 'ip_traffic' in protocol_results:
                ip_traffic = protocol_results['ip_traffic']
                if 'protocols' in ip_traffic:
                    summary.append("Protocol Distribution:")
                    for proto, count in ip_traffic['protocols'].items():
                        summary.append(f"  {proto}: {count}")
                    summary.append("")
        
        self.summary_text.insert(tk.END, "\n".join(summary))
    
    def _display_protocol_results(self, results):
        
        protocol_text = []
        protocol_text.append("=" * 60)
        protocol_text.append("PROTOCOL ANALYSIS")
        protocol_text.append("=" * 60)
        protocol_text.append("")
        
        if 'ip_traffic' in results:
            ip_traffic = results['ip_traffic']
            protocol_text.append("IP Traffic Statistics:")
            protocol_text.append(f"  Total IP Packets: {ip_traffic.get('total_ip_packets', 0)}")
            protocol_text.append("")
            
            if 'protocols' in ip_traffic:
                protocol_text.append("Protocol Distribution:")
                for proto, count in sorted(ip_traffic['protocols'].items(), key=lambda x: x[1], reverse=True):
                    protocol_text.append(f"  {proto}: {count}")
                protocol_text.append("")
            
            if 'top_sources' in ip_traffic:
                protocol_text.append("Top Source IPs:")
                for ip, count in ip_traffic['top_sources'][:10]:
                    protocol_text.append(f"  {ip}: {count} packets")
                protocol_text.append("")
            
            if 'top_destinations' in ip_traffic:
                protocol_text.append("Top Destination IPs:")
                for ip, count in ip_traffic['top_destinations'][:10]:
                    protocol_text.append(f"  {ip}: {count} packets")
                protocol_text.append("")
        
        if 'http_traffic' in results:
            http_traffic = results['http_traffic']
            protocol_text.append("HTTP Traffic:")
            protocol_text.append(f"  Total HTTP Requests: {http_traffic.get('total_requests', 0)}")
            protocol_text.append("")
            
            if 'hosts' in http_traffic:
                protocol_text.append("HTTP Hosts:")
                for host, count in http_traffic['hosts'][:10]:
                    protocol_text.append(f"  {host}: {count} requests")
                protocol_text.append("")
            
                                              
            http_details = []
            if 'requests' in http_traffic:
                http_details.append("HTTP Requests:")
                for req in http_traffic['requests'][:50]:               
                    http_details.append(f"  {req.get('method', 'N/A')} {req.get('uri', 'N/A')}")
                    http_details.append(f"    Host: {req.get('host', 'N/A')}")
                    http_details.append("")
            self.http_text.insert(tk.END, "\n".join(http_details))
        
        if 'dns_traffic' in results:
            dns_traffic = results['dns_traffic']
            protocol_text.append("DNS Traffic:")
            protocol_text.append(f"  Total DNS Queries: {dns_traffic.get('total_queries', 0)}")
            protocol_text.append("")
            
                                            
            dns_details = []
            if 'queries' in dns_traffic:
                dns_details.append("DNS Queries:")
                for query in dns_traffic['queries'][:50]:               
                    dns_details.append(f"  {query.get('qname', 'N/A')} -> {query.get('qtype', 'N/A')}")
            self.dns_text.insert(tk.END, "\n".join(dns_details))
        
        self.protocol_text.insert(tk.END, "\n".join(protocol_text))
    
                                     
    
    def create_flows_tab(self):
        
        flows_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(flows_frame, text="🔄 Flows")
        
        title = ttk.Label(flows_frame, text="Network Flow Analysis", style='Title.TLabel')
        title.pack(pady=10)
        
                        
        file_frame = ttk.LabelFrame(flows_frame, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.flows_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.flows_file_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_flows_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_flows_btn = ttk.Button(file_frame, text="Extract Flows", command=self.extract_flows)
        analyze_flows_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(file_frame, text="Export CSV", command=self.export_flows_csv)
        export_btn.pack(side=tk.LEFT, padx=5)
        
                      
        display_frame = ttk.LabelFrame(flows_frame, text="Flow Details", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
                            
        tree_frame = ttk.Frame(display_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('src_ip', 'src_port', 'dst_ip', 'dst_port', 'protocol', 'packets', 'bytes', 'duration')
        self.flows_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.flows_tree.heading(col, text=col.replace('_', ' ').title())
            self.flows_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.flows_tree.yview)
        self.flows_tree.configure(yscrollcommand=scrollbar.set)
        
        self.flows_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
                         
        stats_frame = ttk.LabelFrame(flows_frame, text="Flow Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.flow_stats_text = scrolledtext.ScrolledText(stats_frame, height=5, wrap=tk.WORD)
        self.flow_stats_text.pack(fill=tk.X)
    
    def browse_flows_file(self):
        
        filename = filedialog.askopenfilename(
            filetypes=[("PCAP files", "*.pcap *.pcapng"), ("All files", "*.*")]
        )
        if filename:
            self.flows_file_var.set(filename)
    
    def extract_flows(self):
        
        pcap_file = self.flows_file_var.get()
        if not pcap_file or not os.path.exists(pcap_file):
            messagebox.showerror("Error", "Please select a valid PCAP file")
            return
        
        self.update_status("Extracting flows...")
        
        thread = threading.Thread(target=self._extract_flows_thread, args=(pcap_file,), daemon=True)
        thread.start()
    
    def _extract_flows_thread(self, pcap_file):
        
        try:
            flow_analyzer = FlowAnalyzer(pcap_file)
            flows = flow_analyzer.extract_flows()
            flow_stats = flow_analyzer.get_flow_statistics()
            
                       
            self.root.after(0, lambda: self._display_flows(flows, flow_stats))
            self.root.after(0, lambda: self.update_status(f"Extracted {len(flows)} flows"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def _display_flows(self, flows, stats):
        
                              
        for item in self.flows_tree.get_children():
            self.flows_tree.delete(item)
        
                   
        for flow in flows[:1000]:                                       
            self.flows_tree.insert('', tk.END, values=(
                flow.get('src_ip', 'N/A'),
                flow.get('src_port', 'N/A'),
                flow.get('dst_ip', 'N/A'),
                flow.get('dst_port', 'N/A'),
                flow.get('protocol', 'N/A'),
                flow.get('packets', 0),
                flow.get('bytes', 0),
                f"{flow.get('duration', 0):.2f}s" if flow.get('duration') else 'N/A'
            ))
        
                            
        stats_text = []
        stats_text.append("Flow Statistics:")
        stats_text.append(f"  Total Flows: {stats.get('total_flows', 0)}")
        stats_text.append(f"  Total Packets: {stats.get('total_packets', 0)}")
        stats_text.append(f"  Total Bytes: {stats.get('total_bytes', 0):,}")
        stats_text.append(f"  Average Flow Duration: {stats.get('average_flow_duration', 0):.2f} seconds")
        stats_text.append(f"  Average Flow Size: {stats.get('average_flow_size', 0):.2f} bytes")
        
        self.flow_stats_text.delete(1.0, tk.END)
        self.flow_stats_text.insert(tk.END, "\n".join(stats_text))
    
    def export_flows_csv(self):
        
        pcap_file = self.flows_file_var.get()
        if not pcap_file or not os.path.exists(pcap_file):
            messagebox.showerror("Error", "Please select a valid PCAP file")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                flow_analyzer = FlowAnalyzer(pcap_file)
                flow_analyzer.export_to_csv(filename)
                messagebox.showinfo("Success", f"Flows exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
                                         
    
    def create_detection_tab(self):
        
        detection_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(detection_frame, text="🛡️ Detection")
        
        title = ttk.Label(detection_frame, text="Intrusion Detection", style='Title.TLabel')
        title.pack(pady=10)
        
                        
        file_frame = ttk.LabelFrame(detection_frame, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.detection_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.detection_file_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_detection_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        detect_btn = ttk.Button(file_frame, text="Run Detection", command=self.run_detection)
        detect_btn.pack(side=tk.LEFT, padx=5)
        
                         
        results_frame = ttk.LabelFrame(detection_frame, text="Detection Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
                 
        summary_frame = ttk.Frame(results_frame)
        summary_frame.pack(fill=tk.X, pady=5)
        
        self.detection_summary_text = scrolledtext.ScrolledText(summary_frame, height=5, wrap=tk.WORD)
        self.detection_summary_text.pack(fill=tk.X)
        
                          
        threats_frame = ttk.LabelFrame(results_frame, text="Detected Threats", padding=5)
        threats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        threat_columns = ('severity', 'type', 'source_ip', 'description')
        self.threats_tree = ttk.Treeview(threats_frame, columns=threat_columns, show='headings', height=10)
        
        for col in threat_columns:
            self.threats_tree.heading(col, text=col.replace('_', ' ').title())
            if col == 'description':
                self.threats_tree.column(col, width=400)
            else:
                self.threats_tree.column(col, width=120)
        
        threat_scrollbar = ttk.Scrollbar(threats_frame, orient=tk.VERTICAL, command=self.threats_tree.yview)
        self.threats_tree.configure(yscrollcommand=threat_scrollbar.set)
        
        self.threats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        threat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def browse_detection_file(self):
        
        filename = filedialog.askopenfilename(
            filetypes=[("PCAP files", "*.pcap *.pcapng"), ("All files", "*.*")]
        )
        if filename:
            self.detection_file_var.set(filename)
    
    def run_detection(self):
        
        pcap_file = self.detection_file_var.get()
        if not pcap_file or not os.path.exists(pcap_file):
            messagebox.showerror("Error", "Please select a valid PCAP file")
            return
        
        self.update_status("Running intrusion detection...")
        
        thread = threading.Thread(target=self._run_detection_thread, args=(pcap_file,), daemon=True)
        thread.start()
    
    def _run_detection_thread(self, pcap_file):
        
        try:
            detector = IntrusionDetector(pcap_file)
            threats = detector.detect_anomalies()
            threat_summary = detector.get_threat_summary()
            
                       
            self.root.after(0, lambda: self._display_detection_results(threats, threat_summary))
            self.root.after(0, lambda: self.update_status("Detection complete"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def _display_detection_results(self, threats, summary):
        
                              
        for item in self.threats_tree.get_children():
            self.threats_tree.delete(item)
        
                         
        summary_text = []
        summary_text.append("Detection Summary:")
        summary_text.append(f"  Total Threats: {summary.get('total_threats', 0)}")
        summary_text.append(f"  Total Anomalies: {summary.get('total_anomalies', 0)}")
        summary_text.append(f"  Unique Source IPs: {summary.get('unique_source_ips', 0)}")
        
        self.detection_summary_text.delete(1.0, tk.END)
        self.detection_summary_text.insert(tk.END, "\n".join(summary_text))
        
                         
        for threat in threats:
            self.threats_tree.insert('', tk.END, values=(
                threat.get('severity', 'N/A'),
                threat.get('type', 'N/A'),
                threat.get('source_ip', 'N/A'),
                threat.get('description', 'N/A')
            ))
    
                                             
    
    def create_visualization_tab(self):
        
        viz_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(viz_frame, text="📈 Visualize")
        
        title = ttk.Label(viz_frame, text="Network Visualization", style='Title.TLabel')
        title.pack(pady=10)
        
                        
        file_frame = ttk.LabelFrame(viz_frame, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.viz_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.viz_file_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_viz_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
                               
        options_frame = ttk.LabelFrame(viz_frame, text="Visualization Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.viz_protocol_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Protocol Distribution", variable=self.viz_protocol_var).pack(side=tk.LEFT, padx=10)
        
        self.viz_top_ips_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Top IPs", variable=self.viz_top_ips_var).pack(side=tk.LEFT, padx=10)
        
        self.viz_flows_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Flow Analysis", variable=self.viz_flows_var).pack(side=tk.LEFT, padx=10)
        
        generate_btn = ttk.Button(options_frame, text="Generate Visualizations", command=self.generate_visualizations)
        generate_btn.pack(side=tk.LEFT, padx=10)
        
                          
        output_frame = ttk.LabelFrame(viz_frame, text="Output Directory", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.viz_output_var = tk.StringVar(value="visualization_output")
        output_entry = ttk.Entry(output_frame, textvariable=self.viz_output_var, width=50)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_output_btn = ttk.Button(output_frame, text="Browse", command=self.browse_viz_output)
        browse_output_btn.pack(side=tk.LEFT, padx=5)
        
                
        self.viz_status_text = scrolledtext.ScrolledText(viz_frame, height=10, wrap=tk.WORD)
        self.viz_status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def browse_viz_file(self):
        
        filename = filedialog.askopenfilename(
            filetypes=[("PCAP files", "*.pcap *.pcapng"), ("All files", "*.*")]
        )
        if filename:
            self.viz_file_var.set(filename)
    
    def browse_viz_output(self):
        
        directory = filedialog.askdirectory()
        if directory:
            self.viz_output_var.set(directory)
    
    def generate_visualizations(self):
        
        pcap_file = self.viz_file_var.get()
        if not pcap_file or not os.path.exists(pcap_file):
            messagebox.showerror("Error", "Please select a valid PCAP file")
            return
        
        output_dir = self.viz_output_var.get()
        if not output_dir:
            messagebox.showerror("Error", "Please specify an output directory")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        self.update_status("Generating visualizations...")
        self.viz_status_text.delete(1.0, tk.END)
        self.viz_status_text.insert(tk.END, "Generating visualizations...\n")
        
        thread = threading.Thread(target=self._generate_viz_thread, args=(pcap_file, output_dir), daemon=True)
        thread.start()
    
    def _generate_viz_thread(self, pcap_file, output_dir):
        
        try:
            visualizer = NetworkVisualizer(output_dir=output_dir)
            generated_files = []
            
                                   
            if self.viz_protocol_var.get():
                self.root.after(0, lambda: self.viz_status_text.insert(tk.END, "Generating protocol distribution...\n"))
                analyzer = ProtocolAnalyzer(pcap_file)
                analysis_results = analyzer.analyze()
                if 'ip_traffic' in analysis_results and 'protocols' in analysis_results['ip_traffic']:
                    visualizer.plot_protocol_distribution(analysis_results['ip_traffic']['protocols'])
                    generated_files.append("protocol_distribution.png")
            
                     
            if self.viz_top_ips_var.get():
                self.root.after(0, lambda: self.viz_status_text.insert(tk.END, "Generating top IPs visualization...\n"))
                analyzer = ProtocolAnalyzer(pcap_file)
                top_ips = analyzer.get_top_ips(10)
                if top_ips['top_sources']:
                    visualizer.plot_top_ips(top_ips['top_sources'], top_n=10)
                    generated_files.append("top_ips.png")
            
                           
            if self.viz_flows_var.get():
                self.root.after(0, lambda: self.viz_status_text.insert(tk.END, "Generating flow visualizations...\n"))
                flow_analyzer = FlowAnalyzer(pcap_file)
                flows = flow_analyzer.extract_flows()
                if flows:
                    visualizer.plot_flow_duration(flows)
                    visualizer.plot_flow_size(flows)
                    generated_files.append("flow_duration.png")
                    generated_files.append("flow_size.png")
            
                           
            status_msg = f"Visualizations generated successfully!\n"
            status_msg += f"Output directory: {output_dir}\n"
            status_msg += f"Generated files:\n"
            for f in generated_files:
                status_msg += f"  - {f}\n"
            
            self.root.after(0, lambda: self.viz_status_text.insert(tk.END, status_msg))
            self.root.after(0, lambda: self.update_status("Visualizations generated"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Visualizations saved to {output_dir}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.viz_status_text.insert(tk.END, f"Error: {e}\n"))
    
                                       
    
    def create_reports_tab(self):
        
        reports_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(reports_frame, text="📄 Reports")
        
        title = ttk.Label(reports_frame, text="Forensic Report Generation", style='Title.TLabel')
        title.pack(pady=10)
        
                        
        file_frame = ttk.LabelFrame(reports_frame, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.report_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.report_file_var, width=50)
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_report_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
                        
        options_frame = ttk.LabelFrame(reports_frame, text="Report Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.report_html_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="HTML Report", variable=self.report_html_var).pack(side=tk.LEFT, padx=10)
        
        self.report_json_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="JSON Report", variable=self.report_json_var).pack(side=tk.LEFT, padx=10)
        
        self.report_text_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Text Report", variable=self.report_text_var).pack(side=tk.LEFT, padx=10)
        
                          
        output_frame = ttk.LabelFrame(reports_frame, text="Output Directory", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.report_output_var = tk.StringVar(value="report_output")
        output_entry = ttk.Entry(output_frame, textvariable=self.report_output_var, width=50)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_output_btn = ttk.Button(output_frame, text="Browse", command=self.browse_report_output)
        browse_output_btn.pack(side=tk.LEFT, padx=5)
        
        generate_report_btn = ttk.Button(output_frame, text="Generate Reports", command=self.generate_reports)
        generate_report_btn.pack(side=tk.LEFT, padx=5)
        
                
        self.report_status_text = scrolledtext.ScrolledText(reports_frame, height=15, wrap=tk.WORD)
        self.report_status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def browse_report_file(self):
        
        filename = filedialog.askopenfilename(
            filetypes=[("PCAP files", "*.pcap *.pcapng"), ("All files", "*.*")]
        )
        if filename:
            self.report_file_var.set(filename)
    
    def browse_report_output(self):
        
        directory = filedialog.askdirectory()
        if directory:
            self.report_output_var.set(directory)
    
    def generate_reports(self):
        
        pcap_file = self.report_file_var.get()
        if not pcap_file or not os.path.exists(pcap_file):
            messagebox.showerror("Error", "Please select a valid PCAP file")
            return
        
        output_dir = self.report_output_var.get()
        if not output_dir:
            messagebox.showerror("Error", "Please specify an output directory")
            return
        
        Path(output_dir).mkdir(exist_ok=True)
        
        self.update_status("Generating reports...")
        self.report_status_text.delete(1.0, tk.END)
        self.report_status_text.insert(tk.END, "Generating reports...\n")
        
        thread = threading.Thread(target=self._generate_reports_thread, args=(pcap_file, output_dir), daemon=True)
        thread.start()
    
    def _generate_reports_thread(self, pcap_file, output_dir):
        
        try:
                          
            self.root.after(0, lambda: self.report_status_text.insert(tk.END, "Running analysis...\n"))
            
            analyzer = ProtocolAnalyzer(pcap_file)
            analysis_results = analyzer.analyze()
            
            flow_analyzer = FlowAnalyzer(pcap_file)
            flows = flow_analyzer.extract_flows()
            flow_stats = flow_analyzer.get_flow_statistics()
            
            detector = IntrusionDetector(pcap_file)
            threats = detector.detect_anomalies()
            threat_summary = detector.get_threat_summary()
            
                                 
            report_data = {
                'summary': {
                    'total_packets': len(analyzer.packets),
                    'total_flows': len(flows),
                    'total_threats': threat_summary['total_threats'],
                    'total_anomalies': threat_summary['total_anomalies']
                },
                'ip_traffic': analysis_results.get('ip_traffic', {}),
                'threats': detector.threats,
                'anomalies': detector.anomalies,
                'http_traffic': analysis_results.get('http_traffic', {}),
                'dns_traffic': analysis_results.get('dns_traffic', {})
            }
            
                              
            report_gen = ReportGenerator(output_dir=output_dir)
            generated_files = []
            
            if self.report_html_var.get():
                self.root.after(0, lambda: self.report_status_text.insert(tk.END, "Generating HTML report...\n"))
                html_report = report_gen.generate_html_report(report_data)
                generated_files.append(html_report)
            
            if self.report_json_var.get():
                self.root.after(0, lambda: self.report_status_text.insert(tk.END, "Generating JSON report...\n"))
                json_report = report_gen.generate_json_report(report_data)
                generated_files.append(json_report)
            
            if self.report_text_var.get():
                self.root.after(0, lambda: self.report_status_text.insert(tk.END, "Generating text report...\n"))
                text_report = report_gen.generate_text_report(report_data)
                generated_files.append(text_report)
            
                           
            status_msg = f"Reports generated successfully!\n"
            status_msg += f"Output directory: {output_dir}\n"
            status_msg += f"Generated files:\n"
            for f in generated_files:
                status_msg += f"  - {os.path.basename(f)}\n"
            
            self.root.after(0, lambda: self.report_status_text.insert(tk.END, status_msg))
            self.root.after(0, lambda: self.update_status("Reports generated"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Reports saved to {output_dir}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.report_status_text.insert(tk.END, f"Error: {e}\n"))


def main():
    
    root = tk.Tk()
    app = NetworkForensicsGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

