#ifndef __AVERAGE_PREDICTION_MODEL__
#define __AVERAGE_PREDICTION_MODEL__

#include "PredictionModel.h"
#include <vector>

using namespace std;

class AveragePredictionModel: public PredictionModel
{
    public:
    virtual ~AveragePredictionModel();
    virtual void train(const Matrix& trainingM);
    virtual double predict(unsigned int u, unsigned int v);

    private:
    double globalAverage;
    vector<double> uAverages;
    vector<double> vAverages;
};

#endif
