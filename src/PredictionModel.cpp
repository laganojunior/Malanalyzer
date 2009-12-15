#include "PredictionModel.h"
#include <math.h>

double PredictionModel :: RMSE(const vector<vector <double> >& mat,
                               const vector<vector <double> >& matT,
                               const vector<vector <unsigned int> > & uToV,
                               const vector<vector <unsigned int> > & vToU)
{
    double squaredError = 0;
    int numRatings = 0; 
    for (int u = 0; u < uToV.size(); u++)
    {
        for (int j = 0; j < uToV[u].size(); j++)
        {  
            int v = uToV[u][j];
 
            double diff = mat[u][j] - predict(u, v);

            squaredError += diff * diff;
            numRatings ++;
        }
    }

    return sqrt(squaredError / numRatings);
}    
