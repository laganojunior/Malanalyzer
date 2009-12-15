#include "Matrix.h"
#include <cstdlib>


//////////////////////////////////////////////////////////////////////////
// Clears all non-zero entries
//////////////////////////////////////////////////////////////////////////
void Matrix :: clear()
{
    mat.clear();
    uToV.clear();
    numU = 0;
    numV = 0;
}

//////////////////////////////////////////////////////////////////////////
// Randomly partitions the elements of this matrix into two matrices
// depending on some probability. For any non-zero element, with probability p,
// the element is written to the first matrix, otherwise it goes to the
// second
/////////////////////////////////////////////////////////////////////////
void Matrix :: randomSplit(double p, Matrix& mat1, Matrix& mat2)
{
  
    // Clear the input matrices
    mat1.clear();
    mat2.clear();

    mat1.numU = numU;
    mat1.numV = numV;
    mat2.numU = numU;
    mat2.numV = numV;

    mat1.mat.resize(numU);
    mat2.mat.resize(numU);

    mat1.uToV.resize(numU);
    mat2.uToV.resize(numU);

    // Resize the matrices to proper dimensions
    

    for (int i = 0; i < mat.size(); i++)
    {
        for (int j = 0; j < mat[i].size(); j++)
        {
            double randVal = ((double)rand()) / RAND_MAX;

            if (randVal <= p)
            { 
                mat1.mat[i].push_back(mat[i][j]);
                mat1.uToV[i].push_back(uToV[i][j]);
            }
            else
            {
                mat2.mat[i].push_back(mat[i][j]);
                mat2.uToV[i].push_back(uToV[i][j]);
            }
        }
    }
}
