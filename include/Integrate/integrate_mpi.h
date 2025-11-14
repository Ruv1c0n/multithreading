// integrate_mpi.cpp
// MPI-версия ЛР2 — численное интегрирование
// Поддерживаются 4 варианта функций (id 1..4), методы: rect, trap, simp
// Компиляция: через CMake (в проекте) или mpicxx -O3 -std=c++17 integrate_mpi.cpp -o integrate_mpi

#define _USE_MATH_DEFINES
#include <mpi.h>
#include <iostream>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <limits>
#include <string>
#include <vector>
#include <math.h>

using namespace std;

// Подынтегральные функции (копирую логику из OMP-версии)
double f(int id, double x)
{
    switch (id)
    {
    case 1:
        return 1.0 / sqrt(3 + 3 * pow(x, 2)); // 20a
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
                       const string &method);