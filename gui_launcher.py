#!/usr/bin/env python3
"""
SharePoint Online Migration Preflight Scanner - GUI Launcher
=============================================================
Graphical interface for the SPO preflight scanner with form validation,
progress tracking, and configuration management.

Author: 818Ninja Production Tool
Version: 2.1.1
License: MIT
"""

# Version information
__version__ = "2.1.1"
__author__ = "818Ninja"
__license__ = "MIT"

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Try to import PIL for logo support (optional)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import os
import sys
import json
import threading
import subprocess
from pathlib import Path
from datetime import datetime
import re

# Configuration file for storing recent settings
CONFIG_FILE = "scanner_config.json"


class ScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"SharePoint Migration Preflight Scanner v{__version__}")
        self.root.geometry("720x650")
        self.root.resizable(True, True)
        self.root.minsize(720, 500)
        
        # Variables
        self.dest_type = tk.StringVar(value="sharepoint")
        self.spo_url = tk.StringVar()
        self.library_name = tk.StringVar()
        self.scan_path = tk.StringVar()
        self.scanning = False
        self.scan_process = None
        
        # Load previous configuration
        self.load_config()
        
        # Build UI
        self.create_widgets()
        
        # Set window icon if available
        try:
            icon_path = Path(__file__).parent / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
    
    def create_widgets(self):
        """Build all GUI components."""
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main container with padding (inside scrollable frame)
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Logo (only if PIL is available)
        if PIL_AVAILABLE:
            try:
                logo_path = Path(__file__).parent / "images" / "Designer.png"
                if logo_path.exists():
                    # Load and resize the logo
                    logo_image = Image.open(logo_path)
                    # Resize to a reasonable size (e.g., 120x120)
                    logo_image = logo_image.resize((120, 120), Image.Resampling.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(logo_image)
                    
                    logo_label = ttk.Label(main_frame, image=self.logo_photo)
                    logo_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
            except Exception as e:
                # If logo fails to load, just skip it
                pass
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="SharePoint Migration Preflight Scanner",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=1, column=0, columnspan=3, pady=(0, 5))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="Scan files and folders for SharePoint migration issues",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        subtitle_label.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20)
        )
        
        # === SECTION 1: Scan Mode (FIRST - determines what fields are shown) ===
        row = 4
        section_label = ttk.Label(main_frame, text="1. Select Scan Mode", font=("Segoe UI", 10, "bold"))
        section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        row += 1
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, padx=(20, 0), pady=(0, 5))
        
        self.inventory_mode = tk.BooleanVar(value=False)
        
        ttk.Radiobutton(
            mode_frame,
            text="Pre-Flight Check (Scan for SharePoint migration issues)",
            variable=self.inventory_mode,
            value=False,
            command=self.on_scan_mode_change
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(
            mode_frame,
            text="Inventory Only (Create complete file/folder list with counts)",
            variable=self.inventory_mode,
            value=True,
            command=self.on_scan_mode_change
        ).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        row += 1
        self.mode_help_label = ttk.Label(
            main_frame,
            text="Pre-Flight: Validates files against SharePoint limits and naming rules • Inventory: Lists all files/folders for pre/post migration comparison",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        self.mode_help_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        # === SECTION 2: Destination Type (Hidden in Inventory mode) ===
        row += 1
        self.dest_section_label = ttk.Label(main_frame, text="2. Select Destination Type", font=("Segoe UI", 10, "bold"))
        self.dest_section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        row += 1
        self.dest_frame = ttk.Frame(main_frame)
        self.dest_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, padx=(20, 0), pady=(0, 15))
        
        ttk.Radiobutton(
            self.dest_frame,
            text="SharePoint Online Document Library (/sites/)",
            variable=self.dest_type,
            value="sharepoint",
            command=self.on_dest_type_change
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(
            self.dest_frame,
            text="Microsoft Teams Channel (/teams/)",
            variable=self.dest_type,
            value="teams",
            command=self.on_dest_type_change
        ).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(
            self.dest_frame,
            text="OneDrive for Business",
            variable=self.dest_type,
            value="onedrive",
            command=self.on_dest_type_change
        ).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # === SECTION 3: SharePoint URL (Hidden in Inventory mode) ===
        row += 1
        self.url_section_label = ttk.Label(main_frame, text="3. SharePoint Site URL", font=("Segoe UI", 10, "bold"))
        self.url_section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        row += 1
        self.url_help_label = ttk.Label(
            main_frame,
            text="Example: https://contoso.sharepoint.com/sites/Team",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        self.url_help_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        row += 1
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.spo_url, width=60)
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.url_entry.bind('<FocusOut>', self.validate_url)
        self.url_entry.bind('<KeyRelease>', self.validate_url)
        
        row += 1
        self.url_status_label = ttk.Label(main_frame, text="", font=("Segoe UI", 8))
        self.url_status_label.grid(row=row, column=0, columnspan=3, sticky=tk.W)
        
        # === SECTION 4: Document Library (Hidden in Inventory mode) ===
        row += 1
        self.lib_section_label = ttk.Label(main_frame, text="4. Document Library / Channel Name", font=("Segoe UI", 10, "bold"))
        self.lib_section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        row += 1
        self.lib_help_label = ttk.Label(
            main_frame,
            text="Example: Shared Documents",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        self.lib_help_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        row += 1
        lib_frame = ttk.Frame(main_frame)
        lib_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        lib_frame.columnconfigure(0, weight=1)
        
        self.library_entry = ttk.Entry(lib_frame, textvariable=self.library_name, width=60)
        self.library_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # === SECTION 5: Scan Path (Always visible) ===
        row += 1
        section_label = ttk.Label(main_frame, text="5. Folder to Scan", font=("Segoe UI", 10, "bold"))
        section_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        row += 1
        path_help_label = ttk.Label(
            main_frame,
            text="Select the local or network folder to scan",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        path_help_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        row += 1
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.scan_path, width=50)
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_folder, width=12)
        browse_btn.grid(row=0, column=1)
        
        # Separator
        row += 1
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )
        
        # === SECTION 6: Scan Button ===
        row += 1
        self.scan_button = ttk.Button(
            main_frame,
            text="START SCAN",
            command=self.start_scan,
            style="Accent.TButton"
        )
        self.scan_button.grid(row=row, column=0, columnspan=3, pady=(5, 10), sticky=(tk.W, tk.E))
        
        # Configure button style
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
        
        # === SECTION 7: Progress ===
        row += 1
        self.progress_label = ttk.Label(main_frame, text="Status: Ready", font=("Segoe UI", 9))
        self.progress_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(5, 5))
        
        row += 1
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate', length=660)
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # === SECTION 8: Log Output ===
        row += 1
        log_label = ttk.Label(main_frame, text="Scan Output:", font=("Segoe UI", 9, "bold"))
        log_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        row += 1
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=6,
            width=80,
            wrap=tk.WORD,
            font=("Consolas", 8),
            state='disabled'
        )
        self.log_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # === SECTION 9: Action Buttons ===
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.open_report_btn = ttk.Button(
            button_frame,
            text="Open Report",
            command=self.open_report,
            state='disabled',
            width=15
        )
        self.open_report_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.open_log_btn = ttk.Button(
            button_frame,
            text="Open Log",
            command=self.open_log,
            state='disabled',
            width=15
        )
        self.open_log_btn.grid(row=0, column=1, padx=5)
        
        clear_log_btn = ttk.Button(
            button_frame,
            text="Clear Output",
            command=self.clear_log,
            width=15
        )
        clear_log_btn.grid(row=0, column=2, padx=5)
        
        # Initialize dest type change
        self.on_dest_type_change()
    
    def on_dest_type_change(self):
        """Update UI based on destination type selection."""
        dest = self.dest_type.get()
        
        if dest == "sharepoint":
            self.url_help_label.config(
                text="Example: https://contoso.sharepoint.com/sites/Team"
            )
            self.lib_help_label.config(
                text="Example: Shared Documents (press Enter for default)"
            )
            self.library_entry.config(state='normal')
            if not self.library_name.get():
                self.library_name.set("Shared Documents")
        
        elif dest == "teams":
            self.url_help_label.config(
                text="Example: https://contoso.sharepoint.com/teams/Marketing"
            )
            self.lib_help_label.config(
                text="Example: General (default Teams channel)"
            )
            self.library_entry.config(state='normal')
            if not self.library_name.get() or self.library_name.get() == "Documents":
                self.library_name.set("General")
        
        elif dest == "onedrive":
            self.url_help_label.config(
                text="Example: https://contoso-my.sharepoint.com"
            )
            self.lib_help_label.config(
                text="Library auto-set to 'Documents' (OneDrive default)"
            )
            self.library_entry.config(state='disabled')
            self.library_name.set("Documents")
        
        # Re-validate URL
        self.validate_url()
    
    def on_scan_mode_change(self):
        """Update UI when scan mode is changed (Pre-Flight vs Inventory)."""
        is_inventory = self.inventory_mode.get()
        
        if is_inventory:
            # INVENTORY MODE: Hide SharePoint-related fields
            self.mode_help_label.config(
                text="📋 Inventory mode: Creates complete list of all files/folders with counts (no issue checking). SharePoint URL not required.",
                foreground="blue"
            )
            # Hide destination type section
            self.dest_section_label.grid_remove()
            self.dest_frame.grid_remove()
            # Hide SharePoint URL section
            self.url_section_label.grid_remove()
            self.url_help_label.grid_remove()
            self.url_entry.master.grid_remove()
            self.url_status_label.grid_remove()
            # Hide library section
            self.lib_section_label.grid_remove()
            self.lib_help_label.grid_remove()
            self.library_entry.master.grid_remove()
        else:
            # PRE-FLIGHT MODE: Show SharePoint-related fields
            self.mode_help_label.config(
                text="Pre-Flight: Validates files against SharePoint limits and naming rules • Inventory: Lists all files/folders for pre/post migration comparison",
                foreground="gray"
            )
            # Show destination type section
            self.dest_section_label.grid()
            self.dest_frame.grid()
            # Show SharePoint URL section
            self.url_section_label.grid()
            self.url_help_label.grid()
            self.url_entry.master.grid()
            self.url_status_label.grid()
            # Show library section
            self.lib_section_label.grid()
            self.lib_help_label.grid()
            self.library_entry.master.grid()
    
    def validate_url(self, event=None):
        """Validate SharePoint URL format in real-time."""
        url = self.spo_url.get().strip()
        
        if not url:
            self.url_status_label.config(text="", foreground="black")
            return
        
        dest = self.dest_type.get()
        is_onedrive = (dest == "onedrive")
        is_teams = (dest == "teams")
        
        # Basic checks
        if not url.startswith('https://'):
            self.url_status_label.config(text="⚠ URL must start with 'https://'", foreground="red")
            return
        
        if '.sharepoint.com' not in url.lower():
            self.url_status_label.config(text="⚠ URL must contain '.sharepoint.com'", foreground="red")
            return
        
        # OneDrive specific
        if is_onedrive:
            if '-my.sharepoint.com' not in url.lower():
                self.url_status_label.config(
                    text="⚠ OneDrive URL must contain '-my.sharepoint.com'",
                    foreground="red"
                )
                return
        else:
            # SharePoint/Teams specific
            if '-my.sharepoint.com' in url.lower():
                self.url_status_label.config(
                    text="⚠ This is a OneDrive URL. Select 'OneDrive for Business' instead.",
                    foreground="red"
                )
                return
            
            # Require /sites/ or /teams/ path
            if '/sites/' not in url.lower() and '/teams/' not in url.lower():
                if is_teams:
                    self.url_status_label.config(
                        text="⚠ Teams URL must include '/teams/<name>' path",
                        foreground="red"
                    )
                else:
                    self.url_status_label.config(
                        text="⚠ SharePoint URL must include '/sites/<name>' or '/teams/<name>' path",
                        foreground="red"
                    )
                return
        
        # Valid
        self.url_status_label.config(text="✓ Valid URL", foreground="green")
    
    def browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            title="Select Folder to Scan",
            initialdir=self.scan_path.get() or os.path.expanduser("~")
        )
        if folder:
            self.scan_path.set(folder)
    
    def log(self, message, level="INFO"):
        """Add message to log output."""
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "ERROR":
            tag = "error"
            prefix = "❌"
        elif level == "SUCCESS":
            tag = "success"
            prefix = "✓"
        elif level == "WARNING":
            tag = "warning"
            prefix = "⚠"
        else:
            tag = "info"
            prefix = "ℹ"
        
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
        # Configure tags
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="black")
    
    def clear_log(self):
        """Clear log output."""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def validate_inputs(self):
        """Validate all form inputs before starting scan."""
        # Check if in inventory mode (doesn't need SharePoint URL)
        is_inventory = self.inventory_mode.get()
        
        if not is_inventory:
            # Pre-Flight mode: Require SharePoint URL
            url = self.spo_url.get().strip()
            if not url:
                messagebox.showerror("Validation Error", "SharePoint URL is required for Pre-Flight checks.")
                return False
            
            if self.url_status_label.cget("foreground") == "red":
                messagebox.showerror("Validation Error", "Please fix the SharePoint URL error.")
                return False
            
            # Check library (for non-OneDrive)
            if self.dest_type.get() != "onedrive":
                library = self.library_name.get().strip()
                if not library:
                    messagebox.showerror("Validation Error", "Document Library name is required.")
                    return False
        
        # Check scan path (required for both modes)
        path = self.scan_path.get().strip()
        if not path:
            messagebox.showerror("Validation Error", "Scan path is required.")
            return False
        
        if not os.path.exists(path):
            messagebox.showerror("Validation Error", f"Path does not exist:\n{path}")
            return False
        
        if not os.path.isdir(path):
            messagebox.showerror("Validation Error", f"Path is not a directory:\n{path}")
            return False
        
        return True
    
    def start_scan(self):
        """Start the scanner in a background thread."""
        if self.scanning:
            # Stop scan
            if messagebox.askyesno("Stop Scan", "Are you sure you want to stop the scan?"):
                self.stop_scan()
            return
        
        # Validate inputs
        if not self.validate_inputs():
            return
        
        # Save configuration
        self.save_config()
        
        # Update UI
        self.scanning = True
        self.scan_button.config(text="STOP SCAN", style="Danger.TButton")
        self.progress_label.config(text="Status: Scanning...")
        self.progress_bar.start(10)
        self.open_report_btn.config(state='disabled')
        self.open_log_btn.config(state='disabled')
        
        # Clear previous log
        self.clear_log()
        self.log("Starting scan...", "INFO")
        
        # Build command
        python_exe = sys.executable
        script_path = Path(__file__).parent / "spo_preflight.py"
        
        # Output paths
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            desktop = Path.home() / "OneDrive" / "Desktop"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Check if inventory mode
        if self.inventory_mode.get():
            self.report_path = desktop / f"SPOMigrationInventory_{timestamp}.csv"
            self.log_path = desktop / f"SPOMigrationLog_Inventory_{timestamp}.txt"
        else:
            self.report_path = desktop / f"SPOMigrationReport_{timestamp}.csv"
            self.log_path = desktop / f"SPOMigrationLog_{timestamp}.txt"
        
        cmd = [
            python_exe,
            str(script_path),
            self.scan_path.get().strip(),
            "--log", str(self.log_path),
            "--progress"
        ]
        
        # Add SharePoint URL only if in Pre-Flight mode
        if not self.inventory_mode.get():
            cmd.extend([
                "--spo-url", self.spo_url.get().strip(),
                "--spo-library", self.library_name.get().strip()
            ])
        
        # Add inventory-only flag if checked
        if self.inventory_mode.get():
            cmd.extend(["--inventory-only", "--inventory-report", str(self.report_path)])
        else:
            cmd.extend(["--report", str(self.report_path)])
        
        # Add OneDrive flag if needed
        if self.dest_type.get() == "onedrive":
            cmd.append("--onedrive")
        
        self.log(f"Command: {' '.join(cmd)}", "INFO")
        
        # Start scanner in thread
        def run_scan():
            try:
                self.scan_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Read output line by line
                for line in self.scan_process.stdout:
                    line = line.strip()
                    if line:
                        self.root.after(0, self.log, line, "INFO")
                
                # Wait for completion
                self.scan_process.wait()
                exit_code = self.scan_process.returncode
                
                # Update UI on completion
                self.root.after(0, self.on_scan_complete, exit_code)
                
            except Exception as e:
                self.root.after(0, self.log, f"Error: {str(e)}", "ERROR")
                self.root.after(0, self.on_scan_complete, 1)
        
        # Start thread
        scan_thread = threading.Thread(target=run_scan, daemon=True)
        scan_thread.start()
    
    def stop_scan(self):
        """Stop the running scan."""
        if self.scan_process:
            self.scan_process.terminate()
            self.log("Scan stopped by user", "WARNING")
        
        self.on_scan_complete(None)
    
    def on_scan_complete(self, exit_code):
        """Handle scan completion."""
        self.scanning = False
        self.scan_button.config(text="START SCAN", style="Accent.TButton")
        self.progress_bar.stop()
        self.open_report_btn.config(state='normal')
        self.open_log_btn.config(state='normal')
        
        # Check if this was an inventory scan
        is_inventory = self.inventory_mode.get()
        
        if exit_code is None:
            self.progress_label.config(text="Status: Scan stopped")
        elif exit_code == 0:
            if is_inventory:
                self.progress_label.config(text="Status: Inventory completed ✓")
                self.log("Inventory scan completed successfully.", "SUCCESS")
                
                # Ask to open inventory
                if messagebox.askyesno(
                    "Inventory Complete",
                    "Inventory scan completed successfully!\n\nWould you like to open the inventory report?"
                ):
                    self.open_report()
            else:
                self.progress_label.config(text="Status: Scan completed - No issues found ✓")
                self.log("Scan completed successfully. No issues found.", "SUCCESS")
                messagebox.showinfo(
                    "Scan Complete",
                    "Scan completed successfully!\n\nNo issues found."
                )
        elif exit_code == 10:
            self.progress_label.config(text="Status: Scan completed - Issues found ⚠")
            self.log("Scan completed. Issues found - check report.", "WARNING")
            
            # Ask to open report
            if messagebox.askyesno(
                "Scan Complete",
                "Scan completed with issues found.\n\nWould you like to open the report?"
            ):
                self.open_report()
        else:
            self.progress_label.config(text=f"Status: Scan failed (exit code {exit_code}) ❌")
            self.log(f"Scan failed with exit code {exit_code}", "ERROR")
            messagebox.showerror(
                "Scan Failed",
                f"Scan failed with exit code {exit_code}.\n\nCheck the log for details."
            )
    
    def open_report(self):
        """Open the CSV report in default application."""
        if hasattr(self, 'report_path') and self.report_path.exists():
            try:
                os.startfile(str(self.report_path))
                self.log(f"Opening report: {self.report_path}", "INFO")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open report:\n{str(e)}")
        else:
            messagebox.showwarning("No Report", "No report file found. Run a scan first.")
    
    def open_log(self):
        """Open the log file in default application."""
        if hasattr(self, 'log_path') and self.log_path.exists():
            try:
                os.startfile(str(self.log_path))
                self.log(f"Opening log: {self.log_path}", "INFO")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open log:\n{str(e)}")
        else:
            messagebox.showwarning("No Log", "No log file found. Run a scan first.")
    
    def save_config(self):
        """Save current configuration to JSON file."""
        config = {
            "dest_type": self.dest_type.get(),
            "spo_url": self.spo_url.get().strip(),
            "library_name": self.library_name.get().strip(),
            "scan_path": self.scan_path.get().strip(),
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            config_path = Path(__file__).parent / CONFIG_FILE
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except PermissionError:
            print(f"Warning: Cannot save config file ({CONFIG_FILE}). Permission denied.")
        except Exception as e:
            print(f"Warning: Could not save config ({CONFIG_FILE}): {e}")
    
    def load_config(self):
        """Load previous configuration from JSON file."""
        try:
            config_path = Path(__file__).parent / CONFIG_FILE
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Validate config structure
                if not isinstance(config, dict):
                    print(f"Warning: Invalid config file format. Using defaults.")
                    return
                
                self.dest_type.set(config.get("dest_type", "sharepoint"))
                self.spo_url.set(config.get("spo_url", ""))
                self.library_name.set(config.get("library_name", ""))
                self.scan_path.set(config.get("scan_path", ""))
        except json.JSONDecodeError as e:
            print(f"Warning: Corrupted config file ({CONFIG_FILE}). Using defaults. Error: {e}")
        except PermissionError:
            print(f"Warning: Cannot read config file ({CONFIG_FILE}). Permission denied.")
        except Exception as e:
            print(f"Warning: Could not load config ({CONFIG_FILE}): {e}")


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = ScannerGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == '__main__':
    main()
