import tkinter as tk
from tkinter import ttk
from gui.lab_tab import LabTab

PROJECT_DIR = r"D:\multithreading"
BIN_DIR = f"{PROJECT_DIR}\\bin"
INCLUDE_DIR = f"{PROJECT_DIR}\\include"

LABS = {
    "Lab1": {
        "OMP_EXE": f"{BIN_DIR}\\matrix_omp.exe",
        "MPI_EXE": f"{BIN_DIR}\\matrix_mpi.exe",
        "SRC_DIR": f"{PROJECT_DIR}\\src\\Lab1",
        "INCLUDE_DIR": f"{INCLUDE_DIR}\\Lab1"
    },
    "Lab2": {
        "OMP_EXE": f"{BIN_DIR}\\lab2_omp.exe",
        "MPI_EXE": f"{BIN_DIR}\\lab2_mpi.exe",
        "SRC_DIR": f"{PROJECT_DIR}\\src\\Lab2",
        "INCLUDE_DIR": f"{INCLUDE_DIR}\\Lab2"
    },
    "Lab3": {
        "OMP_EXE": f"{BIN_DIR}\\lab3_omp.exe",
        "MPI_EXE": f"{BIN_DIR}\\lab3_mpi.exe",
        "SRC_DIR": f"{PROJECT_DIR}\\src\\Lab3",
        "INCLUDE_DIR": f"{INCLUDE_DIR}\\Lab3"
    }
}


class MatrixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторные работы MPI / OpenMP")
        self.root.geometry("1100x800")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        for name, info in LABS.items():
            tab = LabTab(notebook, name, info, PROJECT_DIR)
            notebook.add(tab.frame, text=name)


if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixApp(root)
    root.mainloop()
