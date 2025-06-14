import tkinter as tk

class MessageHandler:
    def __init__(self, root):
        self.root = root
        self.message_frame = None

    def set_message_frame(self, frame):
        self.message_frame = frame

    def show_error(self, message):
        if self.message_frame:
            for widget in self.message_frame.winfo_children():
                widget.destroy()
            error_label = tk.Label(self.message_frame, text=message, fg="red")
            error_label.pack(pady=5)
            self.root.after(3000, error_label.destroy)
        else:
            error_label = tk.Label(self.root, text=message, fg="red")
            error_label.pack(pady=10)
            self.root.after(3000, error_label.destroy)

    def show_success(self, message):
        if self.message_frame:
            for widget in self.message_frame.winfo_children():
                widget.destroy()
            success_label = tk.Label(self.message_frame, text=message, fg="green")
            success_label.pack(pady=5)
            self.root.after(3000, success_label.destroy)
        else:
            success_label = tk.Label(self.root, text=message, fg="green")
            success_label.pack(pady=10)
            self.root.after(3000, success_label.destroy) 