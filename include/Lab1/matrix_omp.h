#pragma once
#include <iostream>
#include <fstream>
#include <chrono>
#include <omp.h>
#include <vector>
#include <filesystem>

// Размер матриц
constexpr int N = 1000;

// Генерация матрицы A[i][j] = i^3 + j
void generateMatrixA(std::vector<std::vector<double>> &A);

// Генерация матрицы B[i][j] = 2*i*j
void generateMatrixB(std::vector<std::vector<double>> &B);

// Умножение матриц C = A*B с использованием OpenMP
void multiplyMatricesOMP(const std::vector<std::vector<double>> &A,
                         const std::vector<std::vector<double>> &B,
                         std::vector<std::vector<double>> &C);
