import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json

CONFIG_FILE = "config.json"

class NekoBoardGUI:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.root.title("NekoBoard - Virtual Soundboard")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Sound slots: dict of hotkey -> {file_path, display_name}
        self.slots = {}
        
        # Load saved config
        self.load_config()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top frame for status
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(top_frame, text="NekoBoard Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        
        # Main frame with listbox and buttons
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox to show sounds
        self.listbox = tk.Listbox(main_frame, height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = tk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        # Button frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        add_btn = tk.Button(btn_frame, text="➕ Add Sound", command=self.add_sound)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        self.remove_btn = tk.Button(btn_frame, text="❌ Remove Selected", command=self.remove_sound, state=tk.DISABLED)
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        setkey_btn = tk.Button(btn_frame, text="🎹 Set Hotkey", command=self.set_hotkey)
        setkey_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind listbox selection
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Populate listbox from config
        self.refresh_listbox()
        
    def on_select(self, event):
        """Enable/disable remove button based on selection"""
        selection = self.listbox.curselection()
        if selection:
            self.remove_btn.config(state=tk.NORMAL)
        else:
            self.remove_btn.config(state=tk.DISABLED)
    
    def refresh_listbox(self):
        """Refresh listbox display from slots dict"""
        self.listbox.delete(0, tk.END)
        for hotkey, data in self.slots.items():
            display = f"{hotkey}: {data['display_name']}"
            self.listbox.insert(tk.END, display)
    
    def add_sound(self):
        """Open file dialog to add a .wav file"""
        file_path = filedialog.askopenfilename(
            title="Select Sound File",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        # Ask for hotkey first (before adding)
        self.status_label.config(text="Press a key to assign to this sound...")
        self.root.update()
        
        hotkey = self.wait_for_hotkey()
        if not hotkey:
            self.status_label.config(text="Hotkey cancelled or invalid. Sound not added.")
            return
        
        # Get display name (filename without extension)
        display_name = os.path.basename(file_path)
        
        # Add to slots
        self.slots[hotkey] = {
            'file_path': file_path,
            'display_name': display_name
        }
        
        # Add to sound manager
        if self.app.sound_manager.add_sound(hotkey, file_path):
            self.status_label.config(text=f"Added '{display_name}' with hotkey '{hotkey}'")
            self.refresh_listbox()
            self.save_config()
        else:
            self.status_label.config(text=f"Failed to load sound file")
    
    def remove_sound(self):
        """Remove selected sound"""
        selection = self.listbox.curselection()
        if not selection:
            return
        
        # Get the display string and extract hotkey
        display_str = self.listbox.get(selection[0])
        hotkey = display_str.split(":")[0].strip()
        
        if hotkey in self.slots:
            del self.slots[hotkey]
            self.app.sound_manager.remove_sound(hotkey)
            self.status_label.config(text=f"Removed sound with hotkey '{hotkey}'")
            self.refresh_listbox()
            self.save_config()
    
    def set_hotkey(self):
        """Assign new hotkey to selected sound"""
        selection = self.listbox.curselection()
        if not selection:
            self.status_label.config(text="Select a sound first")
            return
        
        display_str = self.listbox.get(selection[0])
        old_hotkey = display_str.split(":")[0].strip()
        
        self.status_label.config(text=f"Press new key for this sound...")
        self.root.update()
        
        new_hotkey = self.wait_for_hotkey()
        if not new_hotkey:
            self.status_label.config(text="Hotkey change cancelled")
            return
        
        # Update slots
        data = self.slots.pop(old_hotkey)
        self.slots[new_hotkey] = data
        
        # Update sound manager
        self.app.sound_manager.change_hotkey(old_hotkey, new_hotkey)
        
        self.status_label.config(text=f"Changed hotkey from '{old_hotkey}' to '{new_hotkey}'")
        self.refresh_listbox()
        self.save_config()
    
    def wait_for_hotkey(self):
        """Wait for user to press a key (blocking, but allows GUI updates)"""
        import keyboard
        import time
        
        start_time = time.time()
        timeout = 10  # seconds
        
        while time.time() - start_time < timeout:
            # Check for key presses
            event = keyboard.read_event(suppress=False)
            if event.event_type == keyboard.KEY_DOWN:
                key = event.name
                # Convert special keys to readable format
                if key == 'space':
                    key = 'space'
                elif key == 'enter':
                    key = 'enter'
                # Single character or special key name
                if len(key) == 1 or key in ['space', 'enter', 'tab', 'backspace', 'delete', 'esc']:
                    return key
        
        return None
    
    def save_config(self):
        """Save slots to JSON config"""
        config = {}
        for hotkey, data in self.slots.items():
            config[hotkey] = {
                'file_path': data['file_path'],
                'display_name': data['display_name']
            }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        """Load slots from JSON config"""
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            for hotkey, data in config.items():
                # Verify file still exists
                if os.path.exists(data['file_path']):
                    self.slots[hotkey] = {
                        'file_path': data['file_path'],
                        'display_name': data['display_name']
                    }
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def show_error(self, message):
        """Show error message in GUI"""
        messagebox.showerror("NekoBoard Error", message)
        self.status_label.config(text="Error: " + message[:50])
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def run(self):
        """Start GUI main loop"""
        self.root.mainloop()
