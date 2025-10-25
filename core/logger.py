import datetime
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class UILogger:
    """Логгер с выводом в Tkinter и консоль."""

    def __init__(self, text_widget: ScrolledText = None):
        self.text_widget = text_widget

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        print(formatted)
        if self.text_widget:
            self.text_widget.insert(tk.END, formatted + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.update_idletasks()

    def info(self, msg): self.log(msg, "INFO")
    def warn(self, msg): self.log(msg, "WARN")
    def error(self, msg): self.log(msg, "ERROR")
    def success(self, msg): self.log(msg, "OK")
