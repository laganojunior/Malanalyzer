#include "MalDB.h"
#include <assert.h>
#include "AveragePredictionModel.h"
#include "LinearModel.h"
#include "Matrix.h"
#include <cstdlib>
#include <utility>
#include <algorithm>

using namespace std;

int main() 
{
    srand(time(0));
 
    MalDBReader db(string("Mal.db"));

    int userId = db.getUserId("lelouch9178");
	
    AveragePredictionModel model;

    Matrix fullMatrix = db.getMatrix();

    int numTries = 20;
    double trainingRatio = .5;

    double rmseSum = 0;
   
    for (int i = 0; i < numTries; i++)
    {
        Matrix trainingMatrix;
        Matrix testMatrix;

        fullMatrix.randomSplit(trainingRatio, trainingMatrix, testMatrix);
     
        model.train(trainingMatrix);

        rmseSum += model.RMSE(testMatrix);
    } 

    cout << "RMSE is " << rmseSum / numTries << endl;


    int numBest = 25;

    vector<pair<double, int> > animePredicts;
    animePredicts.resize(db.getNumAnime());

    for (int i = 0; i < db.getNumAnime(); i++)
    {        
        animePredicts[i] = pair<double, int> (model.predict(userId, i), i);
    }

    sort(animePredicts.begin(), animePredicts.end());

    for (int i = 0; i < numBest; i++)
    {
        int j = db.getNumAnime() - i - 1;

        cout << db.getAnimeName(animePredicts[j].second) 
             << " " <<  animePredicts[j].first << endl;
    }

    return 0;
}
