#include "LinearModel.h"
#include <math.h>

LinearModel :: ~LinearModel()
{

}

void LinearModel :: setNumFactors(int numFactors)
{
    this -> numFactors = numFactors;
}

void LinearModel :: setRegularizationParameter(double regularize)
{
    this -> regularize = regularize;
}

void LinearModel :: train(const vector<vector <double> >& mat,
                          const vector<vector <double> >& matT,
                          const vector<vector <unsigned int> >& uToV,
                          const vector<vector <unsigned int> >& vToU)
{
    

}

double LinearModel :: predict(unsigned int u, unsigned int v)
{
    return 0;
}
