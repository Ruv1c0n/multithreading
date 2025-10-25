#include <mpi.h>
#include <iostream>
#include <vector>
#include <chrono>

const int N = 1000;

/**
 * The function generates a matrix A with specified number of rows and columns, populating it with
 * values based on a specific formula.
 *
 * @param A A is a reference to a vector of doubles where the generated matrix will be stored.
 * @param rows The `rows` parameter in the `generateMatrixA` function represents the number of rows in
 * the matrix that you want to generate. It specifies the height or the number of horizontal lines in
 * the matrix.
 * @param cols The `cols` parameter in the `generateMatrixA` function represents the number of columns
 * in the matrix `A` that is being generated. It specifies the width of the matrix.
 */
void generateMatrixA(std::vector<double> &A, int rows, int cols);

/**
 * The function `generateMatrixB` populates a 1D vector representing a 2D matrix with values
 * calculated based on the row and column indices.
 *
 * @param B B is a reference to a vector of doubles where the generated matrix will be stored.
 * @param rows The `rows` parameter in the `generateMatrixB` function represents the number of rows in
 * the matrix `B` that is being generated. It specifies how many rows the matrix will have.
 * @param cols The `cols` parameter in the `generateMatrixB` function represents the number of columns
 * in the matrix `B` that is being generated. It specifies the width of the matrix.
 */
void generateMatrixB(std::vector<double> &B, int rows, int cols);
