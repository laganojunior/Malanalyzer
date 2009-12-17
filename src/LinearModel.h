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
        gradTol = 1e-3;
    }

    virtual ~LinearModel();

    void setNumFactors(int numFactors);
    void setRegularizationParameter(double regularize);
    void setGradientTolerance(double gradTol);

    virtual void train(const Matrix& trainingM);
    virtual double predict(unsigned int u, unsigned int v);
    
    private:

    int numFactors;
    double regularize;
    double gradTol;

    vector<vector<double> > uVecs;
    vector<vector<double> > vVecs;
    double globalAvg;
};

#endif
