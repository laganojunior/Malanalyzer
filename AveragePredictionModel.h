#ifndef __AVERAGE_PREDICTION_MODEL__
#define __AVERAGE_PREDICTION_MODEL__

#include "PredictionModel.h"
#include <vector>

using namespace std;

class AveragePredictionModel: public PredictionModel
{
    public:
    virtual ~AveragePredictionModel();

    virtual void train(const vector<vector <double> >& mat,
                       const vector<vector <double> >& matT,
                       const vector<vector <unsigned int> >& uToV,
                       const vector<vector <unsigned int> >& vToU);
    virtual double predict(unsigned int u, unsigned int v);
    virtual double RMSE(const vector<vector <double> >& mat,
                        const vector<vector <double> >& matT,
                        const vector<vector <unsigned int> >& uToV,
                        const vector<vector <unsigned int> >& vToU);
    
    private:
    double globalAverage;
    vector<double> uAverages;
    vector<double> vAverages;
};

#endif
