# This class represents a lab tab in a GUI application for running experiments, compiling code,
# displaying results in a table, and generating interactive graphs.
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Toplevel
import threading
from core import Compiler, ExperimentRunner, UILogger
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# The `LabTab` class in Python represents a tab for a laboratory experiment interface with methods
# for rebuilding the project, starting experiments, updating a table, and displaying interactive
# graphs.
class LabTab:
    def __init__(self, parent, lab_name, lab_info, project_dir):
        """
        The function initializes various attributes and sets up the user interface for a Python
        program.
        
        :param parent: The `parent` parameter in the `__init__` method is typically a reference to the
        parent widget or window that will contain the UI elements created within the class. It is used
        to place the UI elements within the parent widget or window

        :param lab_name: The `lab_name` parameter in the `__init__` method is used to store the name of
        the laboratory. It is a string that represents the name of the lab
        
        :param lab_info: The `lab_info` parameter seems to be a dictionary containing information
        related to the lab. It is used to initialize the `lab_info` attribute of the class instance
        
        :param project_dir: The `project_dir` parameter in the `__init__` method is used to specify the
        directory where the project files are located. It is a path to the directory where the project
        files for the lab are stored. This parameter is essential for setting up the project
        environment and running experiments within the specified
        """
        self.lab_name = lab_name
        self.lab_info = lab_info
        self.project_dir = project_dir
        self.method_var = tk.StringVar(value="OMP")
        self.current_thread = None
        self.is_running = False

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
        """
        The `_build_ui` function creates a user interface with labels, radio buttons, buttons for
        rebuilding projects and starting experiments, and a table using the `ttk` module in Python.
        """
        tk.Label(self.frame, text=f"{self.lab_name}: выбор метода").pack(
            pady=5)
        for method in ["OMP", "MPI"]:
            tk.Radiobutton(self.frame, text=method,
                           variable=self.method_var, value=method).pack()

        btns = tk.Frame(self.frame)
        btns.pack(pady=10)
        ttk.Button(btns, text="Пересобрать", command=self.rebuild_project).grid(
            row=0, column=0, padx=10)
        ttk.Button(btns, text="Запустить эксперимент(1-28)",
                   command=self.start_experiment).grid(row=0, column=1, padx=10)
        
        # --- Таблица ---
        self.tree = ttk.Treeview(self.frame, columns=(
            "Threads", "Time", "Speedup", "Efficiency"), show="headings", height=10)
        for col, width in zip(("Threads", "Time", "Speedup", "Efficiency"), (100, 150, 150, 150)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(pady=10)

    def rebuild_project(self):
        """
        The function `rebuild_project` starts a new thread to execute the `_rebuild_thread` method in
        the background.
        """
        threading.Thread(target=self._rebuild_thread, daemon=True).start()

    def _rebuild_thread(self):
        """
        This function rebuilds a thread based on the selected method using source and executable files.
        :return: If the `src_file` is not found, the function will return without further execution.
        """
        method = self.method_var.get()
        exe = self.lab_info[f"{method}_EXE"]
        src_dir = self.lab_info["SRC_DIR"]

        src_file = self.compiler.find_source(src_dir, method)
        if not src_file:
            return
        if self.compiler.compile(src_file, exe, method):
            self.logger.success(f"{exe} пересобран успешно из {src_file}")

    def start_experiment(self):
        """
        This Python function `start_experiment` checks if an experiment is already running and prompts
        the user to stop and start a new one or continue with the current one.
        
        :return: If the `choice` is `None` or `False`, the function will return without performing any
        further actions. If the `choice` is `True`, the current process will be stopped, a warning
        message will be logged, and a new experiment thread will be started.
        """
        if self.is_running:
            choice = messagebox.askyesnocancel(
                "Процесс выполняется",
                "Другой эксперимент уже запущен.\n\n"
                "Да — остановить и запустить новый\n"
                "Нет — продолжить текущий\n"
                "Отмена — ничего не делать"
            )
            if choice is None or choice is False:
                return
            else:
                self.is_running = False
                self.logger.warn("⚠ Текущий процесс остановлен пользователем.")
        self.is_running = True
        threading.Thread(target=self._experiment_thread, daemon=True).start()

    def _experiment_thread(self):
        """
        This function runs an experiment using a specified method, updates a table with the results,
        plots the results, and displays a graph window.
        """
        method = self.method_var.get()
        exe = self.lab_info[f"{method}_EXE"]

        threads, times = self.runner.run(exe, method)
        self._update_table(threads, times)
        self.runner.plot_results(method, self.lab_name, threads, times)
        self._show_graph_window(method, threads, times)
        self.is_running = False

    def _update_table(self, threads, times):
        """
        The function `_update_table` deletes existing entries in a tree structure, filters out invalid
        thread-time pairs, calculates and inserts new values based on the valid pairs.
        
        :param threads: Threads is a list containing the number of threads for each entry in your data
        
        :param times: The `times` parameter in the `_update_table` method is a list that contains the
        time values corresponding to each thread in the `threads` list. It is used to filter out any
        threads that have a `None` value for time and then perform calculations based on the valid time
        values
        
        :return: If the `valid` list is empty after filtering out threads with `None` times, then the
        function will return without performing any further operations.
        """
        self.tree.delete(*self.tree.get_children())
        valid = [(t, v) for t, v in zip(threads, times) if v is not None]
        if not valid:
            return

        t1 = valid[0][1]
        for t, val in valid:
            s = t1 / val
            e = s / t
            self.tree.insert("", "end", values=(
                t, f"{val:.4f}", f"{s:.2f}", f"{e:.2f}"))

    # ---------------- ГРАФИК ----------------
    def _show_graph_window(self, method, threads, times):
        """
        This Python function generates an interactive graph based on input data, saves it, and displays
        it to the user.
        
        :param method: Method is the name of the method or algorithm used for the computation
        
        :param threads: Threads represents the number of threads or processes used in a computation. It
        is a list containing the values of the number of threads or processes for which corresponding
        computation times are provided
        
        :param times: The `times` parameter in the `_show_graph_window` method represents the list of
        time values corresponding to different numbers of threads or processes. These time values are
        used to calculate the speedup and efficiency metrics for plotting the graph
        
        :return: If the method `_show_graph_window` is called, it will either return nothing (None) if
        there are no valid data points to plot the graph, or it will save the graph as a PNG file and
        display it to the user.
        """
        valid = [(t, v) for t, v in zip(threads, times) if v is not None]
        if not valid:
            self.logger.warn("⚠ Нет корректных данных для графика.")
            return

        t1 = valid[0][1]
        speedup = [t1 / v for _, v in valid]
        efficiency = [s / p for s, (p, _) in zip(speedup, valid)]

        # --- Сохранение ---
        out_dir = os.path.join(self.project_dir, "results", "graphics")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(
            out_dir, f"{self.lab_name.lower()}_{method.lower()}.png")

        # --- Построение графика ---
        plt.figure(figsize=(9, 5))
        plt.plot([t for t, _ in valid], speedup, "o-", label="Ускорение Sₚ")
        plt.plot([t for t, _ in valid], efficiency, "x-",
                 color="red", label="Эффективность Eₚ")
        plt.xlabel("Количество потоков / процессов")
        plt.ylabel("Значение")
        plt.title(f"Результаты ({method}) — {self.lab_name}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(out_path)
        self.logger.success(f"📈 График сохранён: {out_path}")

        # --- Показ пользователю ---
        plt.show()
