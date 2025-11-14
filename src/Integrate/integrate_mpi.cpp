// integrate_mpi.cpp
// MPI-версия ЛР2 — численное интегрирование
// Поведение и интерфейс сделаны максимально схожими с integrate_omp.cpp
// Сборка: mpicxx -O3 -std=c++17 integrate_mpi.cpp -o integrate_mpi.exe
// Запуск (как в OMP): mpiexec -n <P> ./integrate_mpi.exe rect 1 1000000

#include "integrate_mpi.h"

// ─────────────────────────────────────────────
// Универсальный расчёт диапазона как в OMP
// method: rect/trap/simp
// istart..iend — индексы интервалов (rect),
//                узлов (trap,simp)
// a,b,n,h — как в OMP
// ─────────────────────────────────────────────
double integrate_range(int id,
                       double a, double b,
                       long long n,
                       long long istart, long long iend,
                       const string &method)
{
    double h = (a - b) / n;
    double sum = 0.0;

    if (method == "rect") // прямоугольники
    {
        for (long long i = istart; i <= iend; ++i)
        {
            double x = b + (i + 0.5) * h;
            sum += f(id, x);
        }
        return sum * h;
    }
    else if (method == "trap") // трапеции
    {
        for (long long i = istart; i <= iend; ++i)
        {
            double x = b + i * h;
            double coef = (i == 0 || i == n) ? 0.5 : 1.0;
            sum += coef * f(id, x);
        }
        return sum * h;
    }
    else if (method == "simp") // Симпсон
    {
        for (long long i = istart; i <= iend; ++i)
        {
            double x = b + i * h;
            double coef = 0.0;
            if (i == 0 || i == n)
                coef = 1.0;
            else if (i % 2 == 1)
                coef = 4.0;
            else
                coef = 2.0;
            sum += coef * f(id, x);
        }
        return sum * (h / 3.0);
    }
    return 0.0;
}

// ─────────────────────────────────────────────
// Точка входа
// ─────────────────────────────────────────────
int main(int argc, char *argv[])
{
    MPI_Init(&argc, &argv);

    int rank = 0, size = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 4)
    {
        if (rank == 0)
            cerr << "Usage: ./integrate_mpi <method> <integral_id> <n>\n";
        MPI_Finalize();
        return 1;
    }

    string method_str = argv[1];
    int id = stoi(argv[2]);
    long long n = stoll(argv[3]);

    // Границы интеграла
    double a, b;
    switch (id)
    {
    case 1:
        a = 13.0 / 2.0;
        b = 3.0;
        break;
    case 2:
        a = 2.0 * M_PI / 7.0;
        b = -2.0 * M_PI / 7.0;
        break;
    case 3:
        a = -1.0;
        b = -7.0;
        break;
    case 4:
        a = 2.0 * M_PI;
        b = 0.0;
        break;
    default:
        a = 0.0;
        b = 1.0;
        break;
    }

    // Симпсон требует четное число интервалов
    if (method_str == "simp" && n % 2 != 0)
        n++;

    // swap как в OMP
    double sign = 1.0;
    if (a < b)
    {
        swap(a, b);
        sign = -1.0;
    }

    // Деление диапазона между процессами
    long long total = (method_str == "rect") ? n : n + 1;
    long long base = total / size;
    long long rem = total % size;

    long long local = base + (rank < rem ? 1 : 0);
    long long istart = base * rank + min<long long>(rank, rem);
    long long iend = istart + local - 1;

    MPI_Barrier(MPI_COMM_WORLD);
    double t0 = MPI_Wtime();

    double local_res = (local > 0) ? integrate_range(id, a, b, n, istart, iend, method_str) : 0.0;

    double global_res = 0.0;
    MPI_Reduce(&local_res, &global_res, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0)
    {
        double result = global_res;

        // special case для id==4
        if (id == 4)
            result *= 2.0;

        result *= sign;

        // вывод в файл и на экран
        std::filesystem::create_directories("results/output/");
        std::ofstream fout("results/output/integrate_mpi.txt");
        fout.precision(12);
        fout << result << endl;
        fout.close();

        std::cout.precision(12);
        std::cout << "Time: " << MPI_Wtime() - t0 << std::endl;
    }

    MPI_Finalize();
    return 0;
}