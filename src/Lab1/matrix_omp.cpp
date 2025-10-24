#include "matrix_omp.h"


void generateMatrixA(std::vector<std::vector<double>> &A)
{
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
            A[i][j] = i * i * i + j;
}

void generateMatrixB(std::vector<std::vector<double>> &B)
{
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
            B[i][j] = 2.0 * i * j;
}

void multiplyMatricesOMP(const std::vector<std::vector<double>> &A,
                         const std::vector<std::vector<double>> &B,
                         std::vector<std::vector<double>> &C)
{
#pragma omp parallel for collapse(2)
    for (int i = 0; i < N; ++i)
        for (int j = 0; j < N; ++j)
        {
            double sum = 0.0;
            for (int k = 0; k < N; ++k)
                sum += A[i][k] * B[k][j];
            C[i][j] = sum;
        }
}

int main()
{
    std::vector<std::vector<double>> A(N, std::vector<double>(N));
    std::vector<std::vector<double>> B(N, std::vector<double>(N));
    std::vector<std::vector<double>> C(N, std::vector<double>(N, 0.0));

    generateMatrixA(A);
    generateMatrixB(B);

    auto start = std::chrono::high_resolution_clock::now();
    multiplyMatricesOMP(A, B, C);
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> diff = end - start;
    std::cout << "Time: " << diff.count() << std::endl;

    // Сохранение результата
    std::filesystem::create_directories("results/output/");
    std::ofstream fout("results/output/OMP.txt");
    for (const auto &row : C)
    {
        for (auto val : row)
            fout << val << " ";
        fout << "\n";
    }
    fout.close();

    return 0;
}
