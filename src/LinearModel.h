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

    virtual void train(const vector<vector <double> >& mat,
                       const vector<vector <double> >& matT,
                       const vector<vector <unsigned int> >& uToV,
                       const vector<vector <unsigned int> >& vToU);
    virtual double predict(unsigned int u, unsigned int v);
    
    private:

    int numFactors;
    double regularize;
};

#endif
