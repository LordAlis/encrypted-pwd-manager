import tkinter as tk
import os
from database import Database
from utils.message_utils import MessageHandler
from ui.login_screen import LoginScreen
from ui.dashboard_screen import DashboardScreen
from ui.add_entry_screen import AddEntryScreen
from ui.view_entries_screen import ViewEntriesScreen
from encryption_utils import derive_key, encrypt, decrypt

class EncryptedPasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted Password Manager")
        self.root.geometry("600x450")

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.after(100, self.root.focus_force)

        self.db = Database()
        self.message_handler = MessageHandler(root)
        self.current_master_key = None
        self.vault_entries = []
        self.editing_entry_index = -1

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._init_screens()
        
        self.show_screen("login")
        self.root.after(100, self.login_screen.focus_password_entry)

    def _init_screens(self):
        self.login_screen = LoginScreen(
            self.root,
            self.message_handler,
            self._on_login_success,
            self._on_set_master_password
        )

        self.dashboard_screen = DashboardScreen(
            self.root,
            lambda: self.show_screen("view_entries"),
            lambda: self.show_screen("add_entry")
        )

        self.add_entry_screen = AddEntryScreen(
            self.root,
            self.message_handler,
            self._on_save_entry,
            lambda: self.show_screen("dashboard")
        )

        self.view_entries_screen = ViewEntriesScreen(
            self.root,
            self.message_handler,
            self._on_edit_entry,
            self._on_delete_entry,
            lambda: self.show_screen("dashboard")
        )

    def _on_login_success(self, master_key):
        self.current_master_key = master_key
        self.vault_entries = self.db.load_vault_entries()
        self.show_screen("dashboard")

    def _on_set_master_password(self, master_pass):
        salt = os.urandom(16)
        derived_key_bytes = derive_key(master_pass, salt)
        self.db.save_master_password_data(derived_key_bytes, salt)
        self.current_master_key = derived_key_bytes
        self.message_handler.show_success("Master Password set successfully! You are now logged in.")
        self.vault_entries = self.db.load_vault_entries()
        self.show_screen("dashboard")

    def _on_save_entry(self, site, username, password, entry_id=None):
        encrypted_data = encrypt(password, self.current_master_key.decode('latin-1'))
        if entry_id is not None:
            self.db.update_entry(entry_id, site, username, encrypted_data)
            self.message_handler.show_success("Entry updated successfully!")
        else:
            self.db.save_entry(site, username, encrypted_data)
            self.message_handler.show_success("Entry saved successfully!")
        self.vault_entries = self.db.load_vault_entries()
        self.show_screen("dashboard")

    def _on_edit_entry(self, entry):
        self.editing_entry_index = entry['id']
        self.show_screen("add_entry")

    def _on_delete_entry(self, entry_id):
        self.db.delete_entry(entry_id)
        self.vault_entries = self.db.load_vault_entries()
        self.message_handler.show_success("Entry deleted successfully!")
        self.show_screen("view_entries")

    def show_screen(self, screen_name):
        try:
            self._hide_all()
            if screen_name == "login":
                self.login_screen.create(self.db.load_master_password_data()).pack(fill="both", expand=1)
            elif screen_name == "dashboard":
                self.dashboard_screen.create().pack(fill="both", expand=1)
            elif screen_name == "add_entry":
                editing_entry = None
                if self.editing_entry_index != -1:
                    for entry in self.vault_entries:
                        if entry['id'] == self.editing_entry_index:
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
                            break
                self.add_entry_screen.create(editing_entry).pack(fill="both", expand=1)
            elif screen_name == "view_entries":
                self.view_entries_screen.create(self.vault_entries, self.current_master_key).pack(fill="both", expand=1)

            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            self.message_handler.show_error(f"Error showing screen: {str(e)}")
            try:
                self.dashboard_screen.create().pack(fill="both", expand=1)
            except:
                pass

    def _hide_all(self):
        for widget in self.root.winfo_children():
            widget.pack_forget()

    def on_closing(self):
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptedPasswordManagerApp(root)
    root.mainloop()