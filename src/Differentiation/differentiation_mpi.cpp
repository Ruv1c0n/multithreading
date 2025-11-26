#define _USE_MATH_DEFINES
#include <mpi.h>
#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>
#include <sstream>
#include <filesystem>

double f(double x, double t)
{
    return -x * x + x + 2.0 * t;
}

int main(int argc, char *argv[])
{
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 3)
    {
        if (rank == 0)
            std::cerr << "Usage: mpiexec -n <proc> ./differentiation_mpi <M> <T>\n";
        MPI_Finalize();
        return 1;
    }

    int M = atoi(argv[1]);    // количество разбиений по x
    double T = atof(argv[2]); // конечное время моделирования

    double h = 1.0 / M;
    double tau = h * h / 2.0; // условие устойчивости
    int N = static_cast<int>(T / tau);

    // разбиение области по процессам
    int chunk = M / size;
    int remainder = M % size;
    int start = rank * chunk + std::min(rank, remainder);
    int local_M = chunk + (rank < remainder ? 1 : 0);
    int end = start + local_M - 1;

    // буферы для текущего и следующего шага
    std::vector<double> u(local_M + 2, 0.0); // +2 для граничных соседей
    std::vector<double> u_next(local_M + 2, 0.0);

    // начальные условия
    for (int i = 0; i <= local_M + 1; i++)
        u[i] = 0.0;

    double t0 = MPI_Wtime();
    // основной временной цикл
    for (int n = 0; n < N; n++)
    {
        double t = n * tau;

        // обмен граничными значениями
        double left_send = u[1], right_send = u[local_M];
        double left_recv = 0.0, right_recv = 0.0;

        if (rank > 0)
            MPI_Sendrecv(&u[1], 1, MPI_DOUBLE, rank - 1, 0,
                         &left_recv, 1, MPI_DOUBLE, rank - 1, 0,
                         MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        else
            left_recv = 0.0; // левая граница: u(0, t) = 0

        if (rank < size - 1)
            MPI_Sendrecv(&u[local_M], 1, MPI_DOUBLE, rank + 1, 0,
                         &right_recv, 1, MPI_DOUBLE, rank + 1, 0,
                         MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        else
            // правая граница: u'_x(1, t) = 1  =>  (u[M] - u[M-1]) / h = 1
            right_recv = u[local_M] + h;

        // вычисление внутренних узлов
        for (int i = 1; i <= local_M; i++)
        {
            double x = (start + i - 1) * h;
            double u_left = (i == 1) ? left_recv : u[i - 1];
            double u_right = (i == local_M) ? right_recv : u[i + 1];
            u_next[i] = u[i] + tau / (h * h) * (u_right - 2 * u[i] + u_left) + tau * f(x, t);
        }

        u.swap(u_next);
    }

    // сбор результатов
    std::vector<double> local_result(local_M);
    for (int i = 0; i < local_M; i++)
        local_result[i] = u[i + 1];

    std::vector<int> counts(size), displs(size);
    for (int i = 0; i < size; i++)
    {
        counts[i] = M / size + (i < remainder ? 1 : 0);
        displs[i] = i * chunk + std::min(i, remainder);
    }

    std::vector<double> full_result;
    if (rank == 0)
        full_result.resize(M);

    MPI_Gatherv(local_result.data(), local_M, MPI_DOUBLE,
                full_result.data(), counts.data(), displs.data(), MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    if (rank == 0)
    {
        std::filesystem::create_directories("results/output/");
        std::ofstream fout("results/output/differentiation_mpi.txt");
        fout.precision(12);
        for (int i = 0; i < M; i++)
            fout << i * h << " " << full_result[i] << "\n";
        fout.close();

        std::cout.precision(12);
        double execution_time = MPI_Wtime() - t0;
        std::cout << "Time: " << execution_time << std::endl;
    }

    MPI_Finalize();
    return 0;
}
