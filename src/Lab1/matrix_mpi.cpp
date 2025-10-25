/**
 * The above C++ program uses MPI to parallelize matrix multiplication by distributing matrix A,
 * broadcasting matrix B, performing local block multiplication, and gathering the results.
 */
#include "matrix_mpi.h"


void generateMatrixA(std::vector<double> &A, int rows, int cols)
{
    for (int i = 0; i < rows; ++i)
        for (int j = 0; j < cols; ++j)
            A[i * cols + j] = i * i * i + j;
}

void generateMatrixB(std::vector<double> &B, int rows, int cols)
{
    for (int i = 0; i < rows; ++i)
        for (int j = 0; j < cols; ++j)
            B[i * cols + j] = 2.0 * i * j;
}

/**
 * The function performs matrix multiplication using MPI parallelization with scatter and gather
 * operations.
 * 
 * @param argc The `argc` parameter in the `main` function stands for "argument count" and represents
 * the number of arguments passed to the program when it is executed from the command line. It
 * includes the name of the program itself as the first argument.
 * @param argv The `argv` parameter in the `main` function is an array of strings representing the
 * command-line arguments passed to the program. Each element of the array `argv` contains a
 * null-terminated C-string (char array) representing an argument.
 * 
 * @return The `main` function is returning an integer value of 0. This is a common practice in C and
 * C++ programs to indicate successful execution of the program.
 */
int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    // Каждая матрица хранится в виде одномерного массива
    std::vector<double> A, B, C;
    int rows_per_proc = N / size;

    // Выделяем память под локальные блоки
    std::vector<double> A_local(rows_per_proc * N);
    std::vector<double> C_local(rows_per_proc * N, 0.0);

    auto start = std::chrono::high_resolution_clock::now();

    /* The code snippet `if (rank == 0)` is checking if the current MPI process has rank 0. If the
    rank is 0, it means this process is the root process or the master process in the MPI
    communicator. */
    if (rank == 0)
    {
        A.resize(N * N);
        B.resize(N * N);
        C.resize(N * N);

        generateMatrixA(A, N, N);
        generateMatrixB(B, N, N);
    }

    // Рассылаем части матрицы A
    MPI_Scatter(A.data(), rows_per_proc * N, MPI_DOUBLE,
                A_local.data(), rows_per_proc * N, MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    // Рассылаем всю матрицу B всем процессам
    if (rank != 0)
        B.resize(N * N);
    MPI_Bcast(B.data(), N * N, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // Перемножаем локальные блоки
    for (int i = 0; i < rows_per_proc; ++i)
    {
        for (int j = 0; j < N; ++j)
        {
            double sum = 0.0;
            for (int k = 0; k < N; ++k)
                sum += A_local[i * N + k] * B[k * N + j];
            C_local[i * N + j] = sum;
        }
    }

    // Собираем результат обратно на 0-й процесс
    MPI_Gather(C_local.data(), rows_per_proc * N, MPI_DOUBLE,
               C.data(), rows_per_proc * N, MPI_DOUBLE,
               0, MPI_COMM_WORLD);

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;

    if (rank == 0)
    {
        std::cout << "Time: " << diff.count() << std::endl;
    }

    MPI_Finalize();
    return 0;
}