import tkinter as tk

class DashboardScreen:
    def __init__(self, parent, on_view_entries, on_add_entry):
        self.parent = parent
        self.on_view_entries = on_view_entries
        self.on_add_entry = on_add_entry
        self.frame = None

    def create(self):
        self.frame = tk.Frame(self.parent)
        
        tk.Label(self.frame, text="Dashboard", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Button(
            self.frame, 
            text="View/Edit/Delete Entries", 
            width=30, 
            command=self.on_view_entries,
            font=("Arial", 12)
        ).pack(pady=10)
        
        tk.Button(
            self.frame, 
            text="Add New Entry", 
            width=30, 
            command=self.on_add_entry,
            font=("Arial", 12)
        ).pack(pady=10)

        return self.frame 