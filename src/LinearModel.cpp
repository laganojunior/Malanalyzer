#include "LinearModel.h"
#include "gsl/gsl_multimin.h"
#include <math.h>
#include <iostream>

using namespace std;

//////////////////////////////////////////////////////////////////////
// Helper functions / structs to run the gsl minimization
//////////////////////////////////////////////////////////////////////

struct Parameters
{
    double regularize;
    int numFactors;
    Matrix mat;
};

double errorFunc(const gsl_vector * x, void * params)
{
    Parameters * p = (Parameters *)params;
    const double& regularize = p -> regularize;
    const int&    numFactors = p -> numFactors;
    const Matrix& mat        = p -> mat;

    double error = 0.0;
    int numEntries = 0;

    // Calculate the mean squared error 
    for (int i = 0; i < mat.numU; i++)
    {
        for (int j = 0; j < mat.mat[i].size(); j++)
        {
            double actual = mat.mat[i][j];
            
            int uVecI = i * numFactors;
            int vVecI = mat.numU * numFactors + mat.uToV[i][j] * numFactors;
           
            const double * uVec = gsl_vector_const_ptr(x, uVecI);
            const double * vVec = gsl_vector_const_ptr(x, vVecI); 

            double predict = 0;

            for (int k = 0; k < numFactors; k++)
                predict += uVec[k] * vVec[k];

            double diff = predict - actual;
            error += diff * diff;
            numEntries ++;
        }
    }

    error /= numEntries;

    return error;
}

void gradientFunc(const gsl_vector * x, void * params, gsl_vector * g)
{
    // Initialize all the gradient elements to 0.
    gsl_vector_set_zero(g);

    Parameters * p = (Parameters *)params;
    const double& regularize = p -> regularize;
    const int&    numFactors = p -> numFactors;
    const Matrix& mat        = p -> mat;

    int numEntries = 0;

    // Calculate the gradient terms from the mean squared error 
    for (int i = 0; i < mat.numU; i++)
    {
        for (int j = 0; j < mat.mat[i].size(); j++)
        {
            double actual = mat.mat[i][j];
            
            int uVecI = i * numFactors;
            int vVecI = mat.numU * numFactors + mat.uToV[i][j] * numFactors;
           
            const double * uVec = gsl_vector_const_ptr(x, uVecI);
            const double * vVec = gsl_vector_const_ptr(x, vVecI); 

            double predict = 0;

            for (int k = 0; k < numFactors; k++)
                predict += uVec[k] * vVec[k];

            double diff = predict - actual;
            numEntries ++;

            double diff2 = diff * 2;

            // Add up this term for the u's (this involves multiplying
            // by the appropriate v term) and the v's (which involves
            // multiplying by u terms  
    
            double * uGrad = gsl_vector_ptr(g, uVecI);
            double * vGrad = gsl_vector_ptr(g, vVecI);

            for (int k = 0; k < numFactors; k++)
            {
                uGrad[k] += diff2 * vVec[k];
                vGrad[k] += diff2 * uVec[k];
            }                
        }
    }

    // Average out all the gradient terms
    gsl_vector_scale(g, 1.0 / numEntries);
     
} 

void errorAndGrad(const gsl_vector * x, void * params, double * f,
                  gsl_vector * g)
{
    Parameters * p = (Parameters *)params;
    const double& regularize = p -> regularize;
    const int&    numFactors = p -> numFactors;
    const Matrix& mat        = p -> mat;

    double error = 0.0;
    int numEntries = 0;

    gsl_vector_set_zero(g);

    // Calculate the mean squared error 
    for (int i = 0; i < mat.numU; i++)
    {
        for (int j = 0; j < mat.mat[i].size(); j++)
        {
            double actual = mat.mat[i][j];
            
            int uVecI = i * numFactors;
            int vVecI = mat.numU * numFactors + mat.uToV[i][j] * numFactors;
           
            const double * uVec = gsl_vector_const_ptr(x, uVecI);
            const double * vVec = gsl_vector_const_ptr(x, vVecI); 

            double predict = 0;

            for (int k = 0; k < numFactors; k++)
                predict += uVec[k] * vVec[k];

            double diff = predict - actual;
            error += diff * diff;
            numEntries ++;

            double diff2 = diff * 2;

            // Add up this term for the u's (this involves multiplying
            // by the appropriate v term) and the v's (which involves
            // multiplying by u terms  
    
            double * uGrad = gsl_vector_ptr(g, uVecI);
            double * vGrad = gsl_vector_ptr(g, vVecI);

            for (int k = 0; k < numFactors; k++)
            {
                uGrad[k] += diff2 * vVec[k];
                vGrad[k] += diff2 * uVec[k];
            }
        }
    }

    error /= numEntries;
    *f = error;

    // Average out all the gradient terms
    gsl_vector_scale(g, 1.0 / numEntries);
     
}

//////////////////////////////////////////////////////////////////////////
// LinearModel function definitions
//////////////////////////////////////////////////////////////////////////
 
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
    // Initialize parameters
    Parameters p;
    p.regularize = regularize;
    p.numFactors = numFactors;
    p.mat = trainingM;

    // Initialize the initial point randomly in -1 to 1
    gsl_vector * x = gsl_vector_alloc((trainingM.numU + trainingM.numV) 
                                       * numFactors);

    for (int i = 0; i < (trainingM.numU + trainingM.numV) * numFactors; i++)
    {
        double v = (((float)rand()) / RAND_MAX) * 2.0 - 1.0;
        gsl_vector_set(x, i, v);
    }


    // Train using minimization of error
     
    gsl_multimin_function_fdf objFunc;
    objFunc.n = (trainingM.numU + trainingM.numV) * numFactors;
    objFunc.f = errorFunc;
    objFunc.df = gradientFunc;
    objFunc.fdf = errorAndGrad;
    objFunc.params = &p;

    gsl_multimin_fdfminimizer * minimizer = gsl_multimin_fdfminimizer_alloc(
                           gsl_multimin_fdfminimizer_vector_bfgs2, objFunc.n);

    gsl_multimin_fdfminimizer_set(minimizer, &objFunc, x, .01, 1e-3);

    double gradQuitTol = .01;
    int iter = 0; 
    int status;
    do
    {
        iter++;
        status = gsl_multimin_fdfminimizer_iterate(minimizer);

        if (status)
        {
            cout << "An error occurred?" << endl;
            break;
        }

        status = gsl_multimin_test_gradient(minimizer->gradient, gradQuitTol);
   
        cout << iter << "\t" << minimizer->f << "\t" << endl; 
        if (status == GSL_SUCCESS)
            cout << "Minimum found" << endl;
    } while (status == GSL_CONTINUE);

    gsl_multimin_fdfminimizer_free(minimizer);
    

    // Set u and v vecs

    uVecs.resize(trainingM.numU);

    for (int i = 0; i < trainingM.numU; i++)
    {
        uVecs[i].resize(numFactors);

        for (int j = 0; j < numFactors; j++)
        {
            uVecs[i][j] = gsl_vector_get(x, i * numFactors + j);
        }
    }

    vVecs.resize(trainingM.numV);

    for (int i = 0; i < trainingM.numV; i++)
    {

        vVecs[i].resize(numFactors);

        for (int j = 0; j < numFactors; j++)
        {
            vVecs[i][j] = gsl_vector_get(x, (i + trainingM.numU) 
                                            * numFactors + j);
        }
    } 

    gsl_vector_free(x);
}

double LinearModel :: predict(unsigned int u, unsigned int v)
{
    double score = 0;
    for (int k = 0; k < numFactors; k++)
        score += uVecs[u][k] * vVecs[v][k];

    return score;
}
