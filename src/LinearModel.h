#ifndef __LINEAR_MODEL__
#define __LINEAR_MODEL__

#include "PredictionModel.h"
#include <vector>

using namespace std;

class LinearModel: public PredictionModel
{
    public:
    LinearModel(int numFactors, double regularize)
    {
        this -> numFactors = numFactors;    
        this -> regularize = regularize;
    }

    virtual ~LinearModel();

    void setNumFactors(int numFactors);
    void setRegularizationParameter(double regularize);

    virtual void train(const Matrix& trainingM) = 0;
    virtual double predict(unsigned int u, unsigned int v);
    
    private:

    int numFactors;
    double regularize;
};

#endif
