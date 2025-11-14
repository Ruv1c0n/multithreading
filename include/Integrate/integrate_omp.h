#define _USE_MATH_DEFINES
#include <iostream>
#include <cmath>
#include <omp.h>
#include <math.h>
#include <filesystem>
#include <fstream>
#include <limits>

using namespace std;

// ────────────────────────────────────────────────────────────────
// Подынтегральные функции (варианты интегралов из практикума)
// ────────────────────────────────────────────────────────────────
double f(int id, double x)
{
    switch (id)
    {
    case 1:
        return 1.0 / sqrt(3 + 3 * pow(x, 2)); // 20а
    case 2:
        return exp(x) * sin(exp(x)); // 20b
    case 3:
        return 1.0 / pow(sqrt(pow(x, 2) - 1), 2); // 20c
    case 4:
        return x * atan(x) / sqrt(1 + pow(x, 2)); // 20d
    default:
        return x; // запасной вариант
    }
}

// ────────────────────────────────────────────────────────────────
// Методы интегрирования
// method = 1 — прямоугольников
// method = 2 — трапеций
// method = 3 — Симпсона
// ────────────────────────────────────────────────────────────────
double integrate_omp(int id, double a, double b, int n, int method);
