"""core.compiler
===================

Small helper for compiling example C++ programs used by the labs. The class
wraps invocation of `g++` (and the platform MPI linker on Windows) and logs
progress to the supplied logger.

Quick example
-------------
from core.compiler import Compiler
log = UILogger()
comp = Compiler(include_dir="include/Lab1", logger=log)
src = "src/Lab1/matrix_omp.cpp"
exe = "bin/matrix_omp.exe"
ok = comp.compile(src, exe, method="OMP")
if ok:
    log.success("Binary ready")

Notes
-----
- `compile` uses a 120s timeout and returns ``True`` on success, ``False`` on
  error.
- On Windows the MPI command builds against MS-MPI include/lib paths by
  default. Edit ``_build_command`` if you use a different MPI implementation.
"""

import os
import subprocess
import shutil


class Compiler:
    """Safe, small wrapper to build OMP/MPI test programs.

    Parameters
    - include_dir: path to project include files (passed as -I to the compiler)
    - logger: an object with `.info`, `.warn`, `.error`, `.success` methods
    """

    def __init__(self, include_dir, logger):
        self.include_dir = include_dir
        self.log = logger
        self.check_dependencies()

    def check_dependencies(self):
        """Check for presence of tools used by the helper and warn if missing."""
        for tool in ["g++", "mpiexec"]:
            if not shutil.which(tool):
                self.log.warn(f"Инструмент '{tool}' не найден в PATH.")
        return True

    def find_source(self, src_dir, method):
        """Find a source file ending with ``_{method}.cpp`` in ``src_dir``.

        Returns the absolute path or ``None`` if not found. Logs an error
        on missing file.
        """
        suffix = f"_{method.lower()}.cpp"
        for f in os.listdir(src_dir):
            if f.lower().endswith(suffix):
                return os.path.join(src_dir, f)
        self.log.error(
            f"Не найден файл, оканчивающийся на '{suffix}' в {src_dir}")
        return None

    def compile(self, src_file, exe_file, method):
        """Compile ``src_file`` into ``exe_file``.

        - Uses a 120 second timeout.
        - Logs progress and returns ``True`` on success, ``False`` otherwise.
        """
        if not os.path.exists(src_file):
            self.log.error(f"Исходный файл не найден: {src_file}")
            return False

        cmd = self._build_command(src_file, exe_file, method)
        self.log.info(f"Компиляция {os.path.basename(src_file)} → {exe_file}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            self.log.error("⏱ Время компиляции превышено (120 сек).")
            return False
        except Exception as e:
            self.log.error(f"Ошибка запуска компиляции: {e}")
            return False

        if result.returncode != 0:
            self.log.error(f"Ошибка компиляции:\n{result.stderr}")
            return False

        self.log.success("✅ Компиляция успешна.")
        return True

    def _build_command(self, src, exe, method):
        """Return the command list to invoke the compiler for a given method.

        - For OMP: add ``-fopenmp``.
        - For MPI: use MS-MPI include/lib paths on Windows and link ``-lmsmpi``.
        """
        if method.lower() == "omp":
            return ["g++", "-std=c++17", "-fopenmp", "-O2", src, "-I", self.include_dir, "-o", exe]
        else:
            # Default MS-MPI paths for Windows; change if your MPI differs
            mpi_inc = r"C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
            mpi_lib = r"C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64"
            return [
                "g++", "-std=c++17", "-O2",
                "-I", self.include_dir,
                "-I", mpi_inc,
                "-L", mpi_lib,
                src, "-o", exe, "-lmsmpi"
            ]
