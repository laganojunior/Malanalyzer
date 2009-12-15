#include "AveragePredictionModel.h"
#include <math.h>

AveragePredictionModel :: ~AveragePredictionModel()
{

}

void AveragePredictionModel :: train(const Matrix& trainingM)
{
    // Get the global average
    double globalAvg = 0;
    int numRatings = 0;

    for (int i = 0; i < trainingM.mat.size(); i++)
    {
        for (int j = 0; j < trainingM.mat[i].size(); j++)
        {
            globalAvg += trainingM.mat[i][j];
            numRatings += 1;
        }
    }

    globalAvg /= numRatings;

    // Create memory for the averages
    uAverages.resize(trainingM.numU);
    vAverages.resize(trainingM.numV);

    // Set all the column averages to 0. This will be used as an
    // accumulation for the sum of columns
    for (int i = 0; i < trainingM.numV; i++)
    {
        vAverages[i] = 0.0;
    }

    // Count of ratings per column to easily take the average
    vector<int> vCount;
    vCount.resize(trainingM.numV);

    // Go through each row
    for (int u = 0; u < trainingM.uToV.size(); u++)
    {
        // Sum up the row to get the row averages
        double ratingSum = 0;
        for (int i = 0; i < trainingM.uToV[u].size(); i++)
        {
            double rating = trainingM.mat[u][i];
            ratingSum       += rating;

            // Add up this value to its column sum
            vAverages[trainingM.uToV[u][i]] += trainingM.mat[u][i];
            vCount[trainingM.uToV[u][i]] ++;
        }
       
        if (trainingM.uToV[u].size() > 0) 
            uAverages[u] = ratingSum / trainingM.uToV[u].size();
        else
            uAverages[u] = globalAvg;
    }    

    // Post process the column sums to get the column averages
    for (int i = 0; i < trainingM.numV; i++)
    {
        if (vCount[i] > 0)
            vAverages[i] /= vCount[i];
        else
            vAverages[i] = globalAvg;
    }
   
}

double AveragePredictionModel :: predict(unsigned int u, unsigned int v)
{
    return (uAverages[u] + vAverages[v]) / 2;
}

