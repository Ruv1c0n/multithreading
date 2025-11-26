"""core.experiment
====================

Runner for executing OMP/MPI experiment binaries and plotting simple
speedup/efficiency charts. The runner tries to be forgiving: it logs stderr,
handles timeouts and uses ``None`` for runs that failed or timed out.

Quick example
-------------
from core.experiment import ExperimentRunner
log = UILogger()
proj = "."
runner = ExperimentRunner(log, proj)
threads, times = runner.run("bin/matrix_omp.exe", method="OMP", max_threads=8)
runner.plot_results("OMP", "Lab1", threads, times)

Notes
-----
- The binary is expected to print a line containing ``Time: <number>``. The
  parser extracts the first occurrence and converts it to float.
- Per-run timeouts are 60 seconds. Increase if your experiments are longer.
"""

import os
import subprocess
import matplotlib.pyplot as plt


class ExperimentRunner:
    """Run OMP/MPI experiments and build plots.

    Parameters
    - logger: object with `.info`, `.warn`, `.error`, `.success` methods
    - project_dir: base path used for saving result graphics
    """

    def __init__(self, logger, project_dir):
        self.log = logger
        self.project_dir = project_dir

    def run(self, exe_path, method, submethod=None, integral_id=None, max_threads=28):
        """
        Универсальный запуск эксперимента.
        :param exe: путь к бинарнику
        :param method: 'OMP' или 'MPI'
        :param submethod: для Lab2 — 'rect', 'trap', 'simp'
        :param integral_id: для Lab2 — номер интеграла 1..4
        :return: threads, times
        """
        if not os.path.exists(exe_path):
            self.log.error(f"Исполняемый файл не найден: {exe_path}")
            return []

        args = [exe_path]
        if "differentiation" in exe_path:
            args += ["1000", "1.0"]  # M=1000, T=1.0
        elif submethod != None:
            if submethod is None:
                submethod = "rect"
            if integral_id is None:
                integral_id = 1
            args += [submethod, str(integral_id), str(1000000)]

        threads = range(1, max_threads + 1)
        times = []

        for t in threads:
            self.log.info(f"▶ Запуск {method} с {t} потоками...")
            try:
                if method == "OMP":
                    env = os.environ.copy()
                    env["OMP_NUM_THREADS"] = str(t)
                    proc = subprocess.run(
                        args, capture_output=True, text=True, env=env, timeout=60)
                else:
                    proc = subprocess.run(
                        ["mpiexec", "-n", str(t)] + args, capture_output=True, text=True, timeout=10)

                # if proc.stderr:
                #     self.log.warn(proc.stderr.strip() + proc.stderr +
                #                   proc.stdout + str(proc.args) + str(proc.returncode) + str(proc))

                t_val = self._parse_time(proc.stdout)
                if t_val:
                    times.append(t_val)
                    self.log.info(f"Время: {t_val:.4f} сек")
                else:
                    self.log.warn("⚠ Не удалось извлечь время из вывода." + proc.stderr + proc.stdout + str(proc.args) + str(proc.returncode) + str(proc))
                    times.append(None)

            except subprocess.TimeoutExpired:
                self.log.error("⏱ Превышен лимит 60 сек на выполнение.")
                times.append(None)
            except Exception as e:
                self.log.error(f"Ошибка запуска: {e}")
                times.append(None)

        return list(threads), times

    def _parse_time(self, output: str):
        for line in output.splitlines():
            if "Time:" in line:
                try:
                    return float(line.split("Time:")[1].strip())
                except ValueError:
                    return None
        return None

    def plot_results(self, method, lab_name, threads, times):
        valid = [(t, v) for t, v in zip(threads, times) if v is not None]
        if not valid:
            self.log.warn("Нет корректных данных для построения графика.")
            return

        t1 = valid[0][1]
        speedup = [t1 / v for _, v in valid]
        efficiency = [s / p for s, (p, _) in zip(speedup, valid)]

        plt.figure(figsize=(10, 5))
        plt.plot([t for t, _ in valid], speedup, "o-", label="Ускорение Sₚ")
        plt.plot([t for t, _ in valid], efficiency, "x-",
                 label="Эффективность Eₚ", color="red")
        plt.xlabel("Количество потоков / процессов")
        plt.ylabel("Значение")
        plt.title(f"Результаты ({method}) — {lab_name}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        out_dir = os.path.join(self.project_dir, "results", "graphics")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(
            out_dir, f"{lab_name.lower()}_{method.lower()}.png")
        plt.savefig(out_path)
        plt.close()
        self.log.success(f"📈 График сохранён: {out_path}")
