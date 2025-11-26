#include "integrate_omp.h"

// ────────────────────────────────────────────────────────────────
// Методы интегрирования
// method = 1 — прямоугольников
// method = 2 — трапеций
// method = 3 — Симпсона
// ────────────────────────────────────────────────────────────────
double integrate_omp(int id, double a, double b, int n, int method)
{
    double sign = 1.0;
    if (a < b)
    {
        swap(a, b);
        sign = -1.0;
    }
    // if (id == 3 && ((a * a - 1 <= 0.0) || (b * b - 1 <= 0.0)))
    // {
    //     return numeric_limits<double>::infinity();
    // }
    if (method == 3){
        n = 1000;
        if(n % 2 != 0) n++;
    }
    double h = (a - b) / n;
    double sum = 0.0;

    if (method == 1) // прямоугольники по середине
    {
#pragma omp parallel for reduction(+ : sum)
        for (int i = 0; i < n; ++i)
        {
            double x = b + (i + 0.5) * h;
            sum += f(id, x);
        }
        if (id == 4)
            return 2 * sign * h * sum;
        return sign * h * sum;
    }
    else if (method == 2) // трапеции
    {
#pragma omp parallel for reduction(+ : sum)
        for (int i = 0; i < n; ++i)
        {
            double x = b + i * h;
            double fx = f(id, x);
            if (i == 0 || i == n)
                sum += fx / 2.0;
            else
                sum += fx;
        }
        if (id == 4)
            return 2 * sign * h * sum;
        return sign * h * sum;
    }
    else if (method == 3) // Симпсон
    {
        if (n % 2 != 0)
            n++; // Симпсон требует четное число интервалов
#pragma omp parallel for reduction(+ : sum)
        for (int i = 0; i <= n; ++i)
        {
            double x = b + i * h;
            double fx = f(id, x);
            if (i == 0 || i == n)
                sum += fx;
            else if (i % 2 == 1)
                sum += 4 * fx;
            else
                sum += 2 * fx;
        }
        if (id == 4)
            return 2 * sign * h / 3.0 * sum;
        return sign * h / 3.0 * sum;
    }
    return 0.0;
}

// ────────────────────────────────────────────────────────────────
// Точка входа
// Параметры запуска:
// ./integrate_omp <method> <integral_id> <n>
// Пример: ./integrate_omp 2 3 1000000
// ────────────────────────────────────────────────────────────────
int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        cerr << "Usage: ./integrate_omp <method> <integral_id> <n>" << endl;
        cerr << "method: 1-rectangles, 2-trapezoids, 3-simpson" << endl;
        cerr << "integral_id: 1..4 (варианты функции)" << endl;
        return 1;
    }

    int method;
    std::string m = argv[1];
    if (m == "rect")
        method = 1;
    else if (m == "trap")
        method = 2;
    else if (m == "simp")
        method = 3;
    else
        method = 1;
    int id = stoi(argv[2]);
    int n = stoi(argv[3]);

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
        b = 0;
        break;
    default:
        a = 0;
        b = 1;
        break;
    }

    double start = omp_get_wtime();
    double result = integrate_omp(id, a, b, n, method);
    double end = omp_get_wtime();

    std::filesystem::create_directories("results/output/");
    std::ofstream fout("results/output/integrate_omp.txt");
    fout.precision(12);
    fout << result << std::endl;
    fout.close();

    // ──────────────────────────────────────────────
    // Печатаем только то, что нужно для парсинга
    // ──────────────────────────────────────────────
    std::cout.precision(12);
    std::cout << "Time: " << end - start << std::endl;

    return 0;
}
