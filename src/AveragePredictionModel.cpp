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
        
        uAverages[u] = ratingSum / uToV[u].size();
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
    
        vAverages[v] = ratingSum / vToU[v].size();
    }
    
}

double AveragePredictionModel :: predict(unsigned int u, unsigned int v)
{
    return (uAverages[u] + vAverages[v]) / 2;
}

