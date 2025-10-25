# The `MatrixApp` class creates a GUI application using tkinter that displays multiple tabs for
# different laboratory works related to MPI and OpenMP, with each tab containing specific information
# and functionalities.
import tkinter as tk
from tkinter import ttk
from gui.lab_tab import LabTab

# The code snippet you provided is setting up directory paths for a project related to
# multithreading. Here's what each line is doing:
PROJECT_DIR = r"D:\multithreading"
BIN_DIR = f"{PROJECT_DIR}\\bin"
INCLUDE_DIR = f"{PROJECT_DIR}\\include"

# The `LABS` dictionary in the provided code snippet is storing information related to different
# laboratory works. Each key in the dictionary represents a specific lab (e.g., Lab1, Lab2, Lab3),
# and the corresponding value is another dictionary containing details about that lab.
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


# The `MatrixApp` class initializes a GUI application with tabs for different laboratory works.
class MatrixApp:
    def __init__(self, root):
        """
        The function initializes a GUI window with a notebook containing tabs for different lab works.
        
        :param root: The `root` parameter in the `__init__` method is typically a reference to the main
        Tkinter window or frame. It is the root window of your application where all other widgets and
        components will be placed. In this case, it seems to be the main window for displaying a
        notebook interface
        """
        self.root = root
        self.root.title("Лабораторные работы MPI / OpenMP")
        self.root.geometry("1100x800")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        for name, info in LABS.items():
            tab = LabTab(notebook, name, info, PROJECT_DIR)
            notebook.add(tab.frame, text=name)


# The `if __name__ == "__main__":` block in Python is a common idiom used to ensure that the code
# inside it only runs if the script is executed directly (not imported as a module in another
# script).
if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixApp(root)
    root.mainloop()
