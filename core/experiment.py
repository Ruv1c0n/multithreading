import os
import subprocess
import matplotlib.pyplot as plt


class ExperimentRunner:
    """Запускает OMP/MPI эксперименты и строит графики."""

    def __init__(self, logger, project_dir):
        self.log = logger
        self.project_dir = project_dir

    def run(self, exe_path, method, max_threads=28):
        if not os.path.exists(exe_path):
            self.log.error(f"Исполняемый файл не найден: {exe_path}")
            return []

        threads = range(1, max_threads + 1)
        times = []

        for t in threads:
            self.log.info(f"▶ Запуск {method} с {t} потоками...")
            try:
                if method == "OMP":
                    env = os.environ.copy()
                    env["OMP_NUM_THREADS"] = str(t)
                    proc = subprocess.run(
                        [exe_path], capture_output=True, text=True, env=env, timeout=60)
                else:
                    proc = subprocess.run(
                        ["mpiexec", "-n", str(t), exe_path], capture_output=True, text=True, timeout=60)

                if proc.stderr:
                    self.log.warn(proc.stderr.strip())

                t_val = self._parse_time(proc.stdout)
                if t_val:
                    times.append(t_val)
                    self.log.info(f"Время: {t_val:.4f} сек")
                else:
                    self.log.warn("⚠ Не удалось извлечь время из вывода.")
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
