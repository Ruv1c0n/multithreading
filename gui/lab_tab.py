import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from core.compiler import Compiler
from core.experiment import ExperimentRunner
from core.logger import UILogger


class LabTab:
    def __init__(self, parent, lab_name, lab_info, project_dir):
        self.lab_name = lab_name
        self.lab_info = lab_info
        self.project_dir = project_dir
        self.method_var = tk.StringVar(value="OMP")

        # --- UI ---
        self.frame = ttk.Frame(parent)
        self.output = scrolledtext.ScrolledText(
            self.frame, width=110, height=15)
        self.output.pack(pady=10)

        self.logger = UILogger(self.output)
        self.compiler = Compiler(self.lab_info["INCLUDE_DIR"], self.logger)
        self.runner = ExperimentRunner(self.logger, project_dir)

        self._build_ui()

    def _build_ui(self):
        tk.Label(self.frame, text=f"{self.lab_name}: выбор метода").pack(
            pady=5)
        for method in ["OMP", "MPI"]:
            tk.Radiobutton(self.frame, text=method,
                           variable=self.method_var, value=method).pack()

        btns = tk.Frame(self.frame)
        btns.pack(pady=10)
        ttk.Button(btns, text="Пересобрать", command=self.rebuild_project).grid(
            row=0, column=0, padx=10)
        ttk.Button(btns, text="Запустить эксперимент",
                   command=self.start_experiment).grid(row=0, column=1, padx=10)

    def rebuild_project(self):
        threading.Thread(target=self._rebuild_thread, daemon=True).start()

    def _rebuild_thread(self):
        method = self.method_var.get()
        exe = self.lab_info[f"{method}_EXE"]
        src_dir = self.lab_info["SRC_DIR"]

        src_file = self.compiler.find_source(src_dir, method)
        if not src_file:
            return
        if self.compiler.compile(src_file, exe, method):
            self.logger.success(f"{exe} пересобран успешно из {src_file}")

    def start_experiment(self):
        threading.Thread(target=self._experiment_thread, daemon=True).start()

    def _experiment_thread(self):
        method = self.method_var.get()
        exe = self.lab_info[f"{method}_EXE"]
        threads, times = self.runner.run(exe, method)
        self.runner.plot_results(method, self.lab_name, threads, times)
