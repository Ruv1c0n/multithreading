import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import os
import matplotlib.pyplot as plt

PROJECT_DIR = r"D:\multithreading"
BIN_DIR = os.path.join(PROJECT_DIR, "bin")
INCLUDE_DIR = os.path.join(PROJECT_DIR, "include")
MAX_THREADS = 28

# Настройки лабораторных
LABS = {
    "Lab1": {
        "OMP_EXE": os.path.join(BIN_DIR, "matrix_omp.exe"),
        "MPI_EXE": os.path.join(BIN_DIR, "matrix_mpi.exe"),
        "SRC_DIR": os.path.join(PROJECT_DIR, "src", "Lab1"),
        "INCLUDE_DIR": os.path.join(INCLUDE_DIR, "Lab1")
    },
    "Lab2": {
        "OMP_EXE": os.path.join(BIN_DIR, "lab2_omp.exe"),
        "MPI_EXE": os.path.join(BIN_DIR, "lab2_mpi.exe"),
        "SRC_DIR": os.path.join(PROJECT_DIR, "src", "Lab2"),
        "INCLUDE_DIR": os.path.join(INCLUDE_DIR, "Lab2")
    },
    "Lab3": {
        "OMP_EXE": os.path.join(BIN_DIR, "lab3_omp.exe"),
        "MPI_EXE": os.path.join(BIN_DIR, "lab3_mpi.exe"),
        "SRC_DIR": os.path.join(PROJECT_DIR, "src", "Lab3"),
        "INCLUDE_DIR": os.path.join(INCLUDE_DIR, "Lab3")
    }
}


class LabTab:
    def __init__(self, parent, lab_name, exe_paths):
        self.lab_name = lab_name
        self.lab_info = exe_paths
        self.OMP_EXE = exe_paths["OMP_EXE"]
        self.MPI_EXE = exe_paths["MPI_EXE"]
        self.current_exe = None
        self.current_process = None

        self.frame = ttk.Frame(parent)

        # --- Выбор метода ---
        self.method_var = tk.StringVar(value="OMP")
        tk.Label(self.frame, text="Выберите метод решения:").pack(pady=5)
        tk.Radiobutton(self.frame, text="OpenMP", variable=self.method_var,
                       value="OMP", command=self.update_method).pack()
        tk.Radiobutton(self.frame, text="MPI", variable=self.method_var,
                       value="MPI", command=self.update_method).pack()

        # --- Кнопки ---
        button_frame = tk.Frame(self.frame)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Запустить эксперимент (1–28 потоков)",
                  command=self.run_experiment).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Пересобрать проект",
                  command=self.rebuild_all).grid(row=0, column=1, padx=10)

        # --- Лог ---
        self.output_area = scrolledtext.ScrolledText(
            self.frame, width=110, height=15)
        self.output_area.pack(pady=10)

        # --- Таблица ---
        self.tree = ttk.Treeview(self.frame, columns=("Threads", "Time", "Speedup", "Efficiency"),
                                 show="headings", height=10)
        for col, width in zip(("Threads", "Time", "Speedup", "Efficiency"), (100, 150, 150, 150)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(pady=10)

        self.update_method()

    def log(self, text):
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.frame.update()

    def update_method(self):
        method = self.method_var.get()
        self.current_exe = self.OMP_EXE if method == "OMP" else self.MPI_EXE

    def compile_program(self, src_file, exe_file, method):
        try:
            if method == "OMP":
                cmd = ["g++", "-std=c++17", "-fopenmp", "-O2", src_file,
                    "-I", self.lab_info["INCLUDE_DIR"], "-o", exe_file]
            else:
                mpi_include = r"C:\Program Files (x86)\Microsoft SDKs\MPI\Include" 
                mpi_lib = r"C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64" 
                cmd = [
                    "g++", 
                    "-fopenmp", 
                    "-O2", 
                    "-I", 
                    self.lab_info["INCLUDE_DIR"], 
                    "-I",
                    mpi_include, 
                    "-L",
                    mpi_lib, 
                    src_file, 
                    "-o", 
                    exe_file, 
                    "-lmsmpi"
                ]


            # ВРЕМЕННО: Вывод для отладки
            print(f"DEBUG: Команда компиляции для {method}:")
            print(f"DEBUG: {' '.join(cmd)}")

            self.log(f"[BUILD] {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            if stdout:
                self.log(stdout)
            if stderr:
                self.log(stderr)
            return process.returncode == 0
        except Exception as e:
            self.log(f"[ERROR] Ошибка компиляции: {e}")
            return False

    def rebuild_all(self):
        self.log("🔄 Пересборка проекта...")
        method = self.method_var.get().lower()
        exe = self.OMP_EXE if method == "omp" else self.MPI_EXE
        src_dir = self.lab_info["SRC_DIR"]

        cpp_files = [f for f in os.listdir(src_dir) if f.endswith(".cpp")]
        if not cpp_files:
            self.log(f"❌ Нет исходников в {src_dir}")
            return

        target_file = None
        for cpp_file in cpp_files:
            name_lower = cpp_file.lower()
            if name_lower.endswith(f"_{method}.cpp"):
                target_file = os.path.join(src_dir, cpp_file)
                break

        if not target_file:
            self.log(f"❌ Не найден файл '{method}'.")
            return

        self.compile_program(target_file, exe, method)
        self.log(
            f"✅ {os.path.basename(exe)} пересобран из {os.path.basename(target_file)}.\n")

    def run_experiment(self):
        if self.current_process and self.current_process.poll() is None:
            choice = messagebox.askyesnocancel(
                "Процесс выполняется",
                "Другой процесс уже выполняется.\n\n"
                "Да — остановить текущий процесс и начать новый\n"
                "Нет — продолжить текущий процесс"
            )
            if choice is None or choice is False:
                return
            else:
                self.current_process.terminate()
                self.log("⚠ Текущий процесс остановлен")

        method = self.method_var.get()
        exe = self.OMP_EXE if method == "OMP" else self.MPI_EXE
        src_dir = self.lab_info["SRC_DIR"]
        cpp_files = [f for f in os.listdir(src_dir) if f.endswith(".cpp")]
        if not os.path.exists(exe) and cpp_files:
            # компилируем первый cpp файл
            src_file = os.path.join(src_dir, cpp_files[0])
            if not self.compile_program(src_file, exe, method):
                messagebox.showerror("Ошибка", f"Не удалось собрать {exe}")
                return

        threads = list(range(1, MAX_THREADS + 1))
        times = []

        self.output_area.delete("1.0", tk.END)
        self.tree.delete(*self.tree.get_children())
        self.log(f"▶ Запуск эксперимента ({method})...\n")

        for t in threads:
            self.log(f"Threads: {t} ...")
            try:
                if method == "OMP":
                    env = os.environ.copy()
                    env["OMP_NUM_THREADS"] = str(t)
                    self.current_process = subprocess.Popen(
                        [exe],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env
                    )
                else:
                    self.current_process = subprocess.Popen(
                        ["mpiexec", "-n", str(t), exe],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                stdout, stderr = self.current_process.communicate()
                if stderr:
                    self.log("[stderr]\n" + stderr)

                time_val = self.parse_time(stdout, method)
                if time_val:
                    times.append(time_val)
                    self.log(f"Time: {time_val:.4f} s")
                else:
                    times.append(None)
                    self.log("⚠ Не удалось считать время")

            except Exception as e:
                self.log(f"Ошибка: {e}")
                times.append(None)

        self.display_results(method, threads, times)
        self.current_process = None

    def parse_time(self, output, method="OMP"):
        for line in output.splitlines():
            if "Time:" in line:
                try:
                    return float(line.split("Time:")[1].strip())
                except:
                    pass
        return None

    def display_results(self, method, threads, times):
        valid_threads = [t for t, val in zip(
            threads, times) if val is not None]
        valid_times = [val for val in times if val is not None]

        if not valid_times:
            messagebox.showwarning(
                "Ошибка", "Нет корректных данных о времени выполнения.")
            return

        T1 = valid_times[0]
        speedup = [T1 / t for t in valid_times]
        efficiency = [s / p for s, p in zip(speedup, valid_threads)]

        for i in range(len(valid_threads)):
            self.tree.insert("", "end", values=(
                valid_threads[i],
                f"{valid_times[i]:.4f}",
                f"{speedup[i]:.2f}",
                f"{efficiency[i]:.2f}"
            ))

        plt.figure(figsize=(10, 5))
        plt.plot(valid_threads, speedup, marker='o',
                 color='blue', label="Ускорение Sₚ")
        plt.plot(valid_threads, efficiency, marker='x',
                 color='red', label="Эффективность Eₚ")
        plt.title(f"График ускорения и эффективности ({method})")
        plt.xlabel("Количество потоков / процессов")
        plt.ylabel("Значение")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        output_png_dir = os.path.join(PROJECT_DIR, "results", "graphics")
        os.makedirs(output_png_dir, exist_ok=True)
        filename = os.path.join(
            output_png_dir, f"results_{method.lower()}_{self.lab_name.lower()}.png")
        plt.savefig(filename)
        plt.close()
        self.log(f"\n📈 График сохранён в {filename}\n")


class MatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Многолабораторный эксперимент по матрицам")
        self.root.geometry("1000x800")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = {}
        for lab_name, exe_paths in LABS.items():
            tab = LabTab(self.notebook, lab_name, exe_paths)
            self.notebook.add(tab.frame, text=lab_name)
            self.tabs[lab_name] = tab


if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixApp(root)
    root.mainloop()
