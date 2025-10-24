#pragma once
#include "C:/Program Files (x86)/Microsoft SDKs/MPI/Include/mpi.h" 
#include <iostream>
#include <vector>
#include <fstream>
#include <filesystem>

// Размер матриц
constexpr int N = 1000;

// Генерация локальной части матрицы A
void generateLocalMatrixA(std::vector<std::vector<double>> &A, int start_row);

// Генерация полной матрицы B
void generateMatrixB(std::vector<std::vector<double>> &B);

// Умножение локальной части матриц C_local = A_local * B
void multiplyLocalMatrices(const std::vector<std::vector<double>> &A,
                           const std::vector<std::vector<double>> &B,
                           std::vector<std::vector<double>> &C);

// Сбор результатов от всех процессов в C_full на процессе 0
void gatherResults(const std::vector<std::vector<double>> &C_local,
                   std::vector<std::vector<double>> &C_full,
                   int rank, int size, int start_row, int rows_per_proc, int extra);
