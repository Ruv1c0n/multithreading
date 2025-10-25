#include <mpi.h>
#include <iostream>
#include <vector>
#include <chrono>

const int N = 1000; // Размер матриц (можно изменить)

void generateMatrixA(std::vector<double> &A, int rows, int cols);

void generateMatrixB(std::vector<double> &B, int rows, int cols);
