import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Toplevel
import threading
from core import Compiler, ExperimentRunner, UILogger
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


class LabTab:
    def __init__(self, parent, lab_name, lab_info, project_dir):
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
        method = self.method_var.get()
        exe = self.lab_info[f"{method}_EXE"]

        threads, times = self.runner.run(exe, method)
        self._update_table(threads, times)
        self.runner.plot_results(method, self.lab_name, threads, times)
        self._show_graph_window(method, threads, times)
        self.is_running = False

    def _update_table(self, threads, times):
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
        """Строит интерактивный график по полученным данным и сохраняет его."""
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
