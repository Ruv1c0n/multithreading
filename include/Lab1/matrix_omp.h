#pragma once
#include <iostream>
#include <fstream>
#include <chrono>
#include <omp.h>
#include <vector>
#include <filesystem>

constexpr int N = 1000;

/**
 * The function `generateMatrixA` populates a 2D vector `A` with values calculated based on the
 * indices `i` and `j`.
 *
 * @param A A is a 2D vector of doubles that represents a matrix. The function generateMatrixA takes
 * this matrix as a reference parameter and fills it with values based on the formula A[i][j] = i * i
 * * i + j.
 */
void generateMatrixA(std::vector<std::vector<double>> &A);

/**
 * The function generates a matrix B with elements calculated as 2.0 times the product of row index i
 * and column index j.
 *
 * @param B The parameter `B` is a 2D vector of doubles. It represents a matrix where each element
 * `B[i][j]` stores the value `2.0 * i * j`. The function `generateMatrixB` fills this matrix with the
 * calculated values based on the indices `i
 */
void generateMatrixB(std::vector<std::vector<double>> &B);

/**
 * The function `multiplyMatricesOMP` uses OpenMP to parallelize matrix multiplication of matrices A
 * and B, storing the result in matrix C.
 *
 * @param A A is a constant reference to a 2D vector representing the first matrix in the matrix
 * multiplication operation.
 * @param B The `multiplyMatricesOMP` function you provided is a parallelized matrix multiplication
 * function using OpenMP directives. The function takes three parameters:
 * @param C The parameter C is a reference to a 2D vector that will store the result of multiplying
 * matrices A and B. The function `multiplyMatricesOMP` takes two constant references to 2D vectors A
 * and B as input matrices and performs matrix multiplication using OpenMP parallelization, storing
 * the result
 */
void multiplyMatricesOMP(const std::vector<std::vector<double>> &A,
                         const std::vector<std::vector<double>> &B,
                         std::vector<std::vector<double>> &C);
