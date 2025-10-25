import os
import subprocess
import shutil


class Compiler:
    """Класс для безопасной сборки программ под OMP/MPI."""

    def __init__(self, include_dir, logger):
        self.include_dir = include_dir
        self.log = logger
        self.check_dependencies()

    def check_dependencies(self):
        for tool in ["g++", "mpiexec"]:
            if not shutil.which(tool):
                self.log.warn(f"Инструмент '{tool}' не найден в PATH.")
        return True

    def find_source(self, src_dir, method):
        """Находит .cpp файл, заканчивающийся на _method.cpp"""
        suffix = f"_{method.lower()}.cpp"
        for f in os.listdir(src_dir):
            if f.lower().endswith(suffix):
                return os.path.join(src_dir, f)
        self.log.error(
            f"Не найден файл, оканчивающийся на '{suffix}' в {src_dir}")
        return None

    def compile(self, src_file, exe_file, method):
        """Компиляция с ограничением по времени."""
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
        if method.lower() == "omp":
            return ["g++", "-std=c++17", "-fopenmp", "-O2", src, "-I", self.include_dir, "-o", exe]
        else:
            mpi_inc = r"C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
            mpi_lib = r"C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64"
            return [
                "g++", "-std=c++17", "-O2",
                "-I", self.include_dir,
                "-I", mpi_inc,
                "-L", mpi_lib,
                src, "-o", exe, "-lmsmpi"
            ]
