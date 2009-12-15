#ifndef __PREDICTION_MODEL__
#define __PREDICTION_MODEL__

#include <vector>
#include "Matrix.h"

using namespace std;

class PredictionModel
{
    public:
    virtual ~PredictionModel() {} 
    virtual void train(const Matrix& trainingM) = 0;
    virtual double predict(unsigned int u, unsigned int v) = 0;


    double RMSE(const Matrix& testMat);
}; 

#endif
