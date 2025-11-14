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

    // Calculate local rows for each process
    int rows_per_proc = N / size;
    int remainder = N % size;
    int rows_local = (rank < remainder) ? rows_per_proc + 1 : rows_per_proc;
    int displ_local = 0;

    // Calculate displacements for scatter
    std::vector<int> sendcounts(size);
    std::vector<int> displs(size);
    for (int i = 0; i < size; ++i)
    {
        int rows_i = (i < remainder) ? rows_per_proc + 1 : rows_per_proc;
        sendcounts[i] = rows_i * N;
        displs[i] = (i == 0) ? 0 : displs[i - 1] + sendcounts[i - 1];
        if (i == rank)
        {
            displ_local = displs[i];
        }
    }

    // Allocate memory for local blocks
    std::vector<double> A_local(rows_local * N);
    std::vector<double> B;
    std::vector<double> C_local(rows_local * N, 0.0);
    std::vector<double> C;

    auto start = std::chrono::high_resolution_clock::now();

    if (rank == 0)
    {
        std::vector<double> A(N * N);
        B.resize(N * N);
        C.resize(N * N);

        generateMatrixA(A, N, N);
        generateMatrixB(B, N, N);

        // Scatter matrix A using Scatterv for uneven distribution
        MPI_Scatterv(A.data(), sendcounts.data(), displs.data(), MPI_DOUBLE,
                     A_local.data(), rows_local * N, MPI_DOUBLE,
                     0, MPI_COMM_WORLD);
    }
    else
    {
        B.resize(N * N);
        // Scatter matrix A for non-root processes
        MPI_Scatterv(nullptr, nullptr, nullptr, MPI_DOUBLE,
                     A_local.data(), rows_local * N, MPI_DOUBLE,
                     0, MPI_COMM_WORLD);
    }

    // Broadcast entire matrix B to all processes
    MPI_Bcast(B.data(), N * N, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // Multiply local blocks: A_local * B = C_local
    for (int i = 0; i < rows_local; ++i)
    {
        for (int j = 0; j < N; ++j)
        {
            double sum = 0.0;
            for (int k = 0; k < N; ++k)
            {
                sum += A_local[i * N + k] * B[k * N + j];
            }
            C_local[i * N + j] = sum;
        }
    }

    // Gather results back to process 0 using Gatherv
    if (rank == 0)
    {
        C.resize(N * N);
    }

    MPI_Gatherv(C_local.data(), rows_local * N, MPI_DOUBLE,
                C.data(), sendcounts.data(), displs.data(), MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    auto end = std::chrono::high_resolution_clock::now();
    double diff = std::chrono::duration<double>(end - start).count();

    MPI_Barrier(MPI_COMM_WORLD);

    if (rank == 0)
    {
        std::cout << "Time: " << diff << std::endl;

        // Save result
        std::filesystem::create_directories("results/output/");
        std::ofstream fout("results/output/matrix_mpi.txt");
        for (int i = 0; i < N; ++i)
        {
            for (int j = 0; j < N; ++j)
                fout << C[i * N + j] << " ";
            fout << "\n";
        }
        fout.close();
    }

    MPI_Finalize();
    return 0;
}