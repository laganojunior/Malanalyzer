#include "AveragePredictionModel.h"
#include <math.h>

AveragePredictionModel :: ~AveragePredictionModel()
{

}

void AveragePredictionModel :: train(const vector<vector <double> >& mat,
                                     const vector<vector <double> >& matT,
                                     const vector<vector <unsigned int> >& uToV,
                                     const vector<vector <unsigned int> >& vToU)
{
    // Get the global average
    double globalAvg = 0;
    int numRatings = 0;

    for (int i = 0; i < mat.size(); i++)
    {
        for (int j = 0; j < mat[i].size(); j++)
        {
            globalAvg += mat[i][j];
            numRatings += 1;
        }
    }

    globalAvg /= numRatings;

    // For each u, get the means of ratings 
    uAverages.resize(uToV.size());

    for (int u = 0; u < uToV.size(); u++)
    {
        double ratingSum = 0;
        for (int i = 0; i < uToV[u].size(); i++)
        {

            double rating = mat[u][i];
            ratingSum       += rating;
        }
        
        if (uToV[u].size() > 0) 
            uAverages[u] = ratingSum / uToV[u].size();
        else
            uAverages[u] = globalAvg;
    }    

    vAverages.resize(vToU.size());

    // Similarly for each v, get the means of ratings
    for (int v = 0; v < vToU.size(); v++)
    {
        double ratingSum = 0;
        for (int i = 0; i < vToU[v].size(); i++)
        {
            ratingSum += matT[v][i];
        }
    
        if (vToU[v].size() > 0)
            vAverages[v] = ratingSum / vToU[v].size();
        else
            vAverages[v] = globalAvg;
    }
    
}

double AveragePredictionModel :: predict(unsigned int u, unsigned int v)
{
    return (uAverages[u] + vAverages[v]) / 2;
}

