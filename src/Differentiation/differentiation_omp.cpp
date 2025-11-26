#define _USE_MATH_DEFINES
#include <vector>
#include <functional>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <cmath>
#include <omp.h>
#include <algorithm>
#include <iomanip>
#include <cstring>

void solveHeatOMP_fast(int M, double T,
                       const std::function<double(double, double)> &f,
                       std::vector<double> &result)
{
    if (M <= 0) return;

    double h = 1.0 / M;
    double inv_h2 = 1.0 / (h * h);
    double tau = h * h / 2.0;
    int N = std::max(1, (int)std::ceil(T / tau));

    std::vector<double> u0(M + 1, 0.0);
    std::vector<double> u1(M + 1, 0.0);
    std::vector<double> x(M + 1);

    for(int i=0;i<=M;i++) x[i] = i*h;

    u0[0] = u1[0] = 0.0;
    u0[M] = u1[M] = 0.0;

    double *u  = u0.data();
    double *un = u1.data();

    omp_set_dynamic(0);
    int max_threads = omp_get_max_threads();
    int work = M - 1;
    int chunk = std::max(1, work / (max_threads * 8));

    for (int n = 0; n < N; n++)
    {
        double t = n * tau;

        // Один parallel-for, SIMD встроен ВНУТРЬ ТЕГО ЖЕ цикла
        #pragma omp parallel for schedule(static,chunk)
        for (int i = 1; i < M; i++)
        {
            double lap = (u[i+1] - 2.0*u[i] + u[i-1]) * inv_h2;
            un[i] = u[i] + tau*lap + tau*f(x[i], t);
        }

        un[0] = 0.0;
        un[M] = 0.0;

        std::swap(u, un);
    }

    result.resize(M+1);
    std::memcpy(result.data(), u, (M+1)*sizeof(double));
}

double heatSource(double x, double t)
{
    return -x*x + x + 2.0*t;
}

int main()
{
    int M = 1000;
    double T = 0.1;

    std::cout << "OMP threads = " << omp_get_max_threads() << std::endl;

    std::vector<double> u;

    double start = omp_get_wtime();
    solveHeatOMP_fast(M, T, heatSource, u);
    double end = omp_get_wtime();

    std::cout << std::setprecision(12);
    std::cout << "Time: " << (end - start) << std::endl;

    std::filesystem::create_directories("results/output/");
    std::ofstream fout("results/output/differentiation_omp.txt");
    fout << std::setprecision(12);

    double h = 1.0 / M;
    for (int i = 0; i <= M; ++i)
        fout << i*h << " " << u[i] << "\n";
    return 0;
}
