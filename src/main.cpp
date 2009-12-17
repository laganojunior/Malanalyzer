#include "MalDB.h"
#include <assert.h>
#include "AveragePredictionModel.h"
#include "LinearModel.h"
#include "Matrix.h"
#include <cstdlib>
#include <utility>
#include <algorithm>
#include <sstream>

using namespace std;

vector<string> stringSplit(string str)
{
    stringstream ss(str);

    string buf;
    vector<string> parts;

    while (ss >> buf)
        parts.push_back(buf);

    return parts;
}
        
void trainFull(LinearModel& model, Matrix& fullMatrix)
{
    model.train(fullMatrix);
}


double trainCrossValidate(LinearModel model, Matrix& fullMatrix, double ratio,
                          int numTries)
{

    double rmseSum = 0;
   
    for (int i = 0; i < numTries; i++)
    {
        Matrix trainingMatrix;
        Matrix testMatrix;

        fullMatrix.randomSplit(ratio, trainingMatrix, testMatrix);

        model.train(trainingMatrix);

        double error = model.RMSE(testMatrix);
        rmseSum += error;
    } 

    return rmseSum / numTries;
}

void printRecommendations(LinearModel& model, MalDBReader& db,
                          string username, int num)
{
    vector<pair<double, int> > animePredicts;
    animePredicts.resize(db.getNumAnime());

    int userId = db.getUserId(username);

    for (int i = 0; i < db.getNumAnime(); i++)
    {        
        animePredicts[i] = pair<double, int> (model.predict(userId, i), i);
    }

    sort(animePredicts.begin(), animePredicts.end());

    for (int i = 0; i < num; i++)
    {
        int j = db.getNumAnime() - i - 1;

        cout << db.getAnimeName(animePredicts[j].second) 
             << " " <<  animePredicts[j].first << endl;
    }
}


int main() 
{
    srand(time(0));
 
    MalDBReader db(string("Mal.db"));
    Matrix fullMatrix = db.getMatrix();

    LinearModel model(3, 0.0);

    while (true)
    {
        cout << ">>> ";

        string line;
        getline(cin, line);

        vector<string> parts = stringSplit(line);

        if (parts.size() == 0)
            continue;

        if (parts[0] == "quit")
            break;
        else if (parts[0] == "trainFull")
        {
            trainFull(model, fullMatrix);
            cout << "RMSE is " << model.RMSE(fullMatrix) << endl;
        } 
        else if (parts[0] == "trainCross")
        {
            if (parts.size() < 3)
            {
                cout << "Expected 2 arguments. See help\n";
                continue;
            }

            double ratio = atof(parts[1].c_str());
            int numTries = atoi(parts[2].c_str());
                
            double avgError = trainCrossValidate(model, fullMatrix, 
                                                 ratio, numTries);

            cout << "Avg. Error is " << avgError << endl; 
        } 
        else if (parts[0] == "recommend")
        {
            if (parts.size() < 3)
            {
                cout << "Expected 2 arguments. See help\n";
                continue;
            }
            
            string name = parts[1];
            int num = atoi(parts[2].c_str());            
   
            printRecommendations(model, db, name, num);
        } 
        else if (parts[0] == "setRegularize")
        {
            if (parts.size() < 2)
            {
                cout << "Expected 1 argument. See help\n";
                continue;
            }

            double regularize = atof(parts[1].c_str());
            
            model.setRegularizationParameter(regularize);
        }
        else if (parts[0] == "setNumFactors")
        {
            if (parts.size() < 2)
            {
                cout << "Expected 1 argument. See help\n";
                continue;
            }

            int numFactors = atoi(parts[1].c_str());
            
            if (numFactors < 1)
            {
                cout << "Number of factors must be at least 1" << endl;
                continue;
            }
            
            model.setNumFactors(numFactors);
        }
        else if (parts[0] == "setGradTol")
        {
            if (parts.size() < 2)
            {
                cout << "Expected 1 argument. See help\n";
                continue;
            }

            double gradTol = atof(parts[1].c_str());
            
            model.setGradientTolerance(gradTol);
        } 
        else if (parts[0] == "help")
        {
            cout << "Commands Summary\n";
            cout << "quit - quit the program\n";
            cout << "help - prints this help statement\n";
            cout << "trainFull - train on the full matrix\n";
            cout << "trainCross ratio num - run cross validation tests \n"
                 << "                       and print the test RMSE. Does\n"
                 << "                       not modify the current model\n";
            cout << "recommend username num - print the highest recommended\n"
                 << "                         anime for some user\n";
            cout << "setRegularize p - Set the regularization parameter\n";
            cout << "setNumFactors num - Set the number of linear factors\n"
                 << "                    in each feature vector\n";
            cout << "setGradTol tol - Set the gradient tolerance for\n"
                 << "                 stopping minimization\n";
        }
        else
        {
            cout << "Unrecognized command. See help\n";
        }
    } 
    return 0;
}
