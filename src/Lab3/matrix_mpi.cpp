#include "matrix_mpi.h"

void generateLocalMatrixA(std::vector<std::vector<double>> &A, int start_row)
{
    for (int i = 0; i < A.size(); ++i)
        for (int j = 0; j < N; ++j)
            A[i][j] = (start_row + i) * (start_row + i) * (start_row + i) + j;
}

void generateMatrixB(std::vector<std::vector<double>> &B)
{
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
            B[i][j] = 2.0 * i * j;
}

void multiplyLocalMatrices(const std::vector<std::vector<double>> &A,
                           const std::vector<std::vector<double>> &B,
                           std::vector<std::vector<double>> &C)
{
    for (int i = 0; i < A.size(); ++i)
        for (int j = 0; j < N; ++j)
            for (int k = 0; k < N; ++k)
                C[i][j] += A[i][k] * B[k][j];
}

void gatherResults(const std::vector<std::vector<double>> &C_local,
                   std::vector<std::vector<double>> &C_full,
                   int rank, int size, int start_row, int rows_per_proc, int extra)
{
    int N_local = C_local.size();
    if (rank == 0)
    {
        // Копирование своей части
        for (int i = 0; i < N_local; ++i)
            C_full[start_row + i] = C_local[i];

        // Получение данных от остальных процессов
        for (int p = 1; p < size; ++p)
        {
            int p_start = p * rows_per_proc + std::min(p, extra);
            int p_end = p_start + rows_per_proc + (p < extra ? 1 : 0);
            int count = (p_end - p_start) * N;
            std::vector<double> temp(count);

            MPI_Recv(temp.data(), count, MPI_DOUBLE, p, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

            for (int i = 0; i < p_end - p_start; ++i)
                for (int j = 0; j < N; ++j)
                    C_full[p_start + i][j] = temp[i * N + j];
        }

        // Сохранение результата
        std::filesystem::create_directories("results/output/");
        std::ofstream fout("results/output/MPI.txt");
        for (const auto &row : C_full)
        {
            for (auto val : row)
                fout << val << " ";
            fout << "\n";
        }
        fout.close();
    }
    else
    {
        // Отправка локальной части процесса 0
        std::vector<double> temp(N_local * N);
        for (int i = 0; i < N_local; ++i)
            for (int j = 0; j < N; ++j)
                temp[i * N + j] = C_local[i][j];

        MPI_Send(temp.data(), temp.size(), MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
    }
}

int main(int argc, char *argv[])
{
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int rows_per_proc = N / size;
    int extra = N % size;
    int start_row = rank * rows_per_proc + std::min(rank, extra);
    int end_row = start_row + rows_per_proc + (rank < extra ? 1 : 0);

    std::vector<std::vector<double>> A_local(end_row - start_row, std::vector<double>(N));
    std::vector<std::vector<double>> B(N, std::vector<double>(N));
    std::vector<std::vector<double>> C_local(end_row - start_row, std::vector<double>(N, 0.0));

    generateLocalMatrixA(A_local, start_row);
    generateMatrixB(B);

    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    multiplyLocalMatrices(A_local, B, C_local);

    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();

    if (rank == 0)
    {
        std::vector<std::vector<double>> C_full(N, std::vector<double>(N, 0.0));
        gatherResults(C_local, C_full, rank, size, start_row, rows_per_proc, extra);

        // Сохранение времени
        std::ofstream timeFile("results/output/time.txt");
        timeFile << end_time - start_time << std::endl;
        timeFile.close();
    }
    else
    {
        gatherResults(C_local, {}, rank, size, start_row, rows_per_proc, extra);
    }

    MPI_Finalize();
    return 0;
}
