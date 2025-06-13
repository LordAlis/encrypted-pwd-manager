import tkinter as tk
from utils.password_utils import generate_password

class AddEntryScreen:
    def __init__(self, parent, message_handler, on_save, on_back):
        self.parent = parent
        self.message_handler = message_handler
        self.on_save = on_save
        self.on_back = on_back
        self.frame = None
        self.site_entry = None
        self.username_entry = None
        self.password_entry = None
        self.editing_entry = None
        self.visibility_button = None

    def create(self, editing_entry=None):
        self.editing_entry = editing_entry
        self.frame = tk.Frame(self.parent)
        
        tk.Label(self.frame, text="Add New Entry" if not editing_entry else "Edit Entry", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(self.frame, text="Site:").pack(pady=5)
        self.site_entry = tk.Entry(self.frame, width=40)
        self.site_entry.pack(pady=5)
        
        tk.Label(self.frame, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.frame, width=40)
        self.username_entry.pack(pady=5)
        
        password_frame = tk.Frame(self.frame)
        password_frame.pack(pady=5)
        
        tk.Label(password_frame, text="Password:").pack(side=tk.LEFT)
        self.password_entry = tk.Entry(password_frame, show="*", width=40)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        self.visibility_button = tk.Button(
            password_frame,
            text="👁️",
            command=self.toggle_password_visibility,
            width=3
        )
        self.visibility_button.pack(side=tk.LEFT)
        
        tk.Button(self.frame, text="Generate Password", command=self.generate_password).pack(pady=10)
        tk.Button(self.frame, text="Save", command=self.save_entry).pack(pady=10)
        tk.Button(self.frame, text="Go Back to Home", command=self.on_back).pack(pady=10)

        if self.editing_entry:
            self.site_entry.insert(0, self.editing_entry['site'])
            self.username_entry.insert(0, self.editing_entry['username'])
            self.password_entry.insert(0, self.editing_entry['password'])

        return self.frame

    def generate_password(self):
        password = generate_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def toggle_password_visibility(self):
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
            self.visibility_button.config(text="🔒")
        else:
            self.password_entry.config(show='*')
            self.visibility_button.config(text="👁️")

    def save_entry(self):
        site = self.site_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not site or not username or not password:
            self.message_handler.show_error("All fields must be filled.")
            return

        self.on_save(site, username, password, self.editing_entry['id'] if self.editing_entry else None) 