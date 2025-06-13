import tkinter as tk
from encryption_utils import derive_key

class LoginScreen:
    def __init__(self, parent, message_handler, on_login_success, on_set_password):
        self.parent = parent
        self.message_handler = message_handler
        self.on_login_success = on_login_success
        self.on_set_password = on_set_password
        self.frame = None
        self.entry_password = None
        self.master_password_data = None

    def create(self, master_password_data):
        self.master_password_data = master_password_data
        self.frame = tk.Frame(self.parent)
        
        tk.Label(self.frame, text="Master Password", font=("Arial", 16, "bold")).pack(pady=20)
        self.entry_password = tk.Entry(self.frame, show="*", width=40, font=("Arial", 12))
        self.entry_password.pack(pady=10)
        
        if self.master_password_data:
            self.entry_password.bind('<Return>', lambda event: self.check_login())
            tk.Label(self.frame, text="Enter your existing Master Password to login.", fg="gray").pack(pady=5)
            self.login_button = tk.Button(
                self.frame, 
                text="Login", 
                command=self.check_login, 
                cursor='hand2', 
                font=("Arial", 12)
            )
            self.login_button.pack(pady=10)
        else:
            self.entry_password.bind('<Return>', lambda event: self.set_master_password())
            tk.Label(
                self.frame, 
                text="No Master Password set. Please create one to get started.", 
                fg="red", 
                font=("Arial", 10)
            ).pack(pady=5)
            self.set_master_password_button = tk.Button(
                self.frame, 
                text="Set Master Password", 
                command=self.set_master_password, 
                cursor='hand2', 
                font=("Arial", 12)
            )
            self.set_master_password_button.pack(pady=10)

        return self.frame

    def set_master_password(self):
        master_pass = self.entry_password.get()
        if not master_pass:
            self.message_handler.show_error("Master Password cannot be empty.")
            return

        self.on_set_password(master_pass)
        self.entry_password.delete(0, tk.END)

    def check_login(self):
        entered_password = self.entry_password.get()
        if not entered_password:
            self.message_handler.show_error("Please enter your Master Password.")
            return

        if not self.master_password_data:
            self.message_handler.show_error("No master password found. Please set one.")
            return

        stored_salt = self.master_password_data['salt']
        stored_hashed_password = self.master_password_data['hashed_password']

        derived_key_for_check = derive_key(entered_password, stored_salt)

        if derived_key_for_check == stored_hashed_password:
            self.message_handler.show_success("Login successful!")
            self.on_login_success(derived_key_for_check)
            self.entry_password.delete(0, tk.END)
        else:
            self.message_handler.show_error("Incorrect Master Password")

    def focus_password_entry(self):
        if self.entry_password:
            self.entry_password.focus_set() 