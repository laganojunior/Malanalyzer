#ifndef __PREDICTION_MODEL__
#define __PREDICTION_MODEL__

#include <vector>

using namespace std;

class PredictionModel
{
    public:
    virtual ~PredictionModel() {} 
    virtual void train(const vector<vector <double> >& mat,
                       const vector<vector <double> >& matT,
                       const vector<vector <unsigned int> > & uToV,
                       const vector<vector <unsigned int> > & vToU) = 0;
    virtual double predict(unsigned int u, unsigned int v) = 0;


    double RMSE(const vector<vector <double> >& mat,
                const vector<vector <double> >& matT,
                const vector<vector <unsigned int> > & uToV,
                const vector<vector <unsigned int> > & vToU);

}; 

#endif
