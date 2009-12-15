#include "PredictionModel.h"
#include "Matrix.h"
#include <math.h>

double PredictionModel :: RMSE(const Matrix& testMat)
{
    double squaredError = 0;
    int numRatings = 0; 
    for (int u = 0; u < testMat.uToV.size(); u++)
    {
        for (int j = 0; j < testMat.uToV[u].size(); j++)
        {  
            int v = testMat.uToV[u][j];
 
            double diff = testMat.mat[u][j] - predict(u, v);

            squaredError += diff * diff;
            numRatings ++;
        }
    }

    return sqrt(squaredError / numRatings);
}    
