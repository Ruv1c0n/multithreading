# This class defines a logger that logs messages with timestamps and levels to both the console and a
# Tkinter text widget.
import datetime
import tkinter as tk
from tkinter.scrolledtext import ScrolledText


# This class is a logger that outputs messages to both Tkinter GUI and the console.
class UILogger:
    """Логгер с выводом в Tkinter и консоль."""

    def __init__(self, text_widget: ScrolledText = None):
        """
        The function initializes an object with a text widget attribute that defaults to None.
        
        :param text_widget: The `__init__` method you provided is a constructor for a class, and it
        takes a parameter `text_widget` of type `ScrolledText` with a default value of `None`. This
        means that if no value is provided for `text_widget` when creating an instance of the class
        
        :type text_widget: ScrolledText
        """
        self.text_widget = text_widget

    def log(self, message: str, level: str = "INFO"):
        """
        The function logs a message with a specified level and timestamp, displaying it in a text
        widget if available.
        
        :param message: The `message` parameter in the `log` method is a string that represents the
        actual log message that you want to log or display. It could be any information, warning,
        error, or debug message that you want to record or show in the log
        
        :type message: str
        
        :param level: The `level` parameter in the `log` method is used to specify the logging level of
        the message being logged. By default, the logging level is set to "INFO", but you can provide a
        different logging level when calling the `log` method. This allows you to categorize and
        prioritize, defaults to INFO
        
        :type level: str (optional)
        """
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
