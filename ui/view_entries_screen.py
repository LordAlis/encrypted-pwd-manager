import tkinter as tk
from encryption_utils import decrypt

class ViewEntriesScreen:
    def __init__(self, parent, message_handler, on_edit, on_delete, on_back):
        self.parent = parent
        self.message_handler = message_handler
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back
        self.frame = None
        self.entries_listbox = None
        self.vault_entries = []
        self.current_master_key = None
        self.message_label = None
        self.show_password = False
        self.current_password = None

    def create(self, vault_entries, current_master_key):
        self.vault_entries = vault_entries
        self.current_master_key = current_master_key
        self.frame = tk.Frame(self.parent)
        
        tk.Label(self.frame, text="View Entries", font=("Arial", 16, "bold")).pack(pady=20)
        
        list_frame = tk.Frame(self.frame)
        list_frame.pack(pady=10)
        
        self.entries_listbox = tk.Listbox(list_frame, width=50, height=10)
        self.entries_listbox.pack(side=tk.LEFT, padx=5)
        self.entries_listbox.bind('<<ListboxSelect>>', self.on_entry_select)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.entries_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.entries_listbox.yview)
        
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="Edit", command=self.edit_selected_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_selected_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Go Back to Home", command=self.on_back).pack(side=tk.LEFT, padx=5)
        
        details_frame = tk.Frame(self.frame)
        details_frame.pack(pady=5)
        
        self.message_label = tk.Label(details_frame, text="", fg="green")
        self.message_label.pack(side=tk.LEFT)
        
        self.visibility_button = tk.Button(
            details_frame,
            text="👁️",
            command=self.toggle_password_visibility,
            width=3
        )
        self.visibility_button.pack(side=tk.LEFT, padx=5)
        
        self.update_entries_list()
        return self.frame

    def toggle_password_visibility(self):
        if not self.current_password:
            return
            
        self.show_password = not self.show_password
        if self.show_password:
            self.visibility_button.config(text="🔒")
            self.message_label.config(text=self.current_password)
        else:
            self.visibility_button.config(text="👁️")
            self.message_label.config(text=self.current_password.replace(self.current_password.split('\n')[-1], 'Password: ********'))

    def update_entries_list(self):
        self.entries_listbox.delete(0, tk.END)
        if not self.vault_entries:
            self.entries_listbox.insert(tk.END, "No entries saved yet.")
        else:
            for entry in self.vault_entries:
                self.entries_listbox.insert(tk.END, f"{entry['site']} - {entry['username']}")

    def on_entry_select(self, event):
        try:
            selected_index = self.entries_listbox.curselection()
            if selected_index:
                self.display_entry_details(selected_index[0])
        except Exception as e:
            self.message_handler.show_error(f"Error selecting entry: {str(e)}")

    def display_entry_details(self, index):
        try:
            if not self.vault_entries or index >= len(self.vault_entries):
                self.message_handler.show_error("Invalid entry selected")
                return
                
            entry = self.vault_entries[index]
            if not self.current_master_key:
                self.message_handler.show_error("Master key not available")
                return
                
            decrypted_password = decrypt(
                entry['password_enc']['ciphertext'],
                self.current_master_key.decode('latin-1'),
                entry['password_enc']['salt'],
                entry['password_enc']['iv']
            )
            
            details = f"Site: {entry['site']}\nUsername: {entry['username']}\nPassword: ********"
            self.current_password = f"Site: {entry['site']}\nUsername: {entry['username']}\nPassword: {decrypted_password}"
            self.message_label.config(text=details)
            self.show_password = False
            self.visibility_button.config(text="👁️")
        except Exception as e:
            self.message_handler.show_error(f"Error displaying entry details: {str(e)}")

    def edit_selected_entry(self):
        try:
            if not self.vault_entries:
                self.message_handler.show_error("No entries available to edit.")
                return

            selected_index = self.entries_listbox.curselection()
            if not selected_index:
                self.message_handler.show_error("Please select an entry to edit.")
                return

            index = selected_index[0]
            if index < 0 or index >= len(self.vault_entries):
                self.message_handler.show_error("Invalid selection. Please try again.")
                return

            entry = self.vault_entries[index]
            decrypted_password = decrypt(
                entry['password_enc']['ciphertext'],
                self.current_master_key.decode('latin-1'),
                entry['password_enc']['salt'],
                entry['password_enc']['iv']
            )
            
            editing_entry = {
                'id': entry['id'],
                'site': entry['site'],
                'username': entry['username'],
                'password': decrypted_password
            }
            
            self.on_edit(editing_entry)
        except Exception as e:
            self.message_handler.show_error(f"Error editing entry: {str(e)}")

    def delete_selected_entry(self):
        try:
            if not self.vault_entries:
                self.message_handler.show_error("No entries available to delete.")
                return

            selected_index = self.entries_listbox.curselection()
            if not selected_index:
                self.message_handler.show_error("Please select an entry to delete.")
                return

            index = selected_index[0]
            if index < 0 or index >= len(self.vault_entries):
                self.message_handler.show_error("Invalid selection. Please try again.")
                return

            entry = self.vault_entries[index]
            self.on_delete(entry['id'])
        except Exception as e:
            self.message_handler.show_error(f"Error deleting entry: {str(e)}") 