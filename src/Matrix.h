#ifndef __MATRIX__
#define __MATRIX__

#include <vector>

using namespace std;

// This class contains a simple sparse matrix representation
// containing row lists for the matrix and its transpose.

class Matrix
{
    public:
    Matrix()
    {
        numU = 0;
        numV = 0;
    }

    Matrix(vector<vector <double> >& mat,
           vector<vector <unsigned int> >& uToV,
           int numU, int numV)
    {
        this -> mat  = mat;
        this -> uToV = uToV;
        this -> numU = numU;
        this -> numV = numV;
    }

    void clear();
    void randomSplit(double p, Matrix& mat1, Matrix& mat2);
    double getAvg();
    void addConstant(double c);
    
    vector<vector <double> > mat;
    vector<vector <unsigned int> > uToV;
    int numU;
    int numV;
};


#endif
