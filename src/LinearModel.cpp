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


void LinearModel :: train(const Matrix& trainingM)
{
    

}

double LinearModel :: predict(unsigned int u, unsigned int v)
{
    return 0;
}
