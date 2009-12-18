#include "MalDB.h"
#include <assert.h>
#include "AveragePredictionModel.h"
#include "LinearModel.h"
#include "Matrix.h"
#include <cstdlib>
#include <utility>
#include <algorithm>
#include <sstream>
#include <fstream>

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
        cout << i + 1 << " out of " << numTries << endl;

        Matrix trainingMatrix;
        Matrix testMatrix;

        fullMatrix.randomSplit(ratio, trainingMatrix, testMatrix);

        model.train(trainingMatrix);

        double error = model.RMSE(testMatrix);
        rmseSum += error;
    } 

    return rmseSum / numTries;
}

double lineSearchRegularize(LinearModel model, Matrix& fullMatrix, double ratio,
                            int numTries, double start, double end, double tol)
{
    double currStep = (end - start) / 10;

    while ((end - start) / 2 > tol)
    {
        cout << "\n\n Starting on window (" << start << ", " << end << ")\n\n";

        // Evaluate until a min v structure is found
        double prevE2, prevE, currE;

        cout << "On " << start << endl;
        model.setRegularizationParameter(start);
        prevE2 = trainCrossValidate(model, fullMatrix, ratio, numTries);
        cout << "Error is " << prevE2 << endl;

        cout << "On " << start + currStep << endl;
        model.setRegularizationParameter(start + currStep);
        prevE = trainCrossValidate(model, fullMatrix, ratio, numTries);
        cout << "Error is " << prevE << endl;

        double currR = start + currStep * 2;

        if (prevE <= prevE2)
        { 
            cout << "On " << start + currStep * 2<< endl;
            model.setRegularizationParameter(start + currStep * 2);
            currE = trainCrossValidate(model, fullMatrix, ratio, numTries);
            cout << "Error is " << currE << endl;

            while ( (! ((prevE2 >= prevE) && (prevE <= currE))) &&
                    currR < end)
            {
                prevE2 = prevE;
                prevE = currE;
                
                currR += currStep;

                cout << "On " << currR << endl;
                model.setRegularizationParameter(currR);
                currE = trainCrossValidate(model, fullMatrix, ratio, numTries);
                
                cout << "Error is " << currE << endl;
            }
        }

        double minR = currR - currStep; //Backtrack 1 step to get low point of v

        // Make new window
        start = minR - currStep;
        end = minR + currStep;
        currStep /= 10;
    }

    // After the line search is done to some window, return the midpoint
    return (start + end) / 2;
    
}


void printRecommendations(LinearModel& model, MalDBReader& db,
                          string username, int num)
{
    vector<pair<double, int> > animePredicts;
    animePredicts.resize(db.getNumAnime());

    int userId = db.getUserId(username);

    if (userId == -1)
    {
        cout << "User " << username << " not found" << endl;
        return;
    }

    for (int i = 0; i < db.getNumAnime(); i++)
    {        
        animePredicts[i] = pair<double, int> (model.predict(userId, i), i);
    }

    sort(animePredicts.begin(), animePredicts.end());

    const vector<unsigned int>& rated = db.getAnimeRated(userId);

    for (int i = 0; i < num; i++)
    {
        int j = db.getNumAnime() - i - 1;

        int animeId = animePredicts[j].second;

        // Avoid anything the user has already rated
        bool found = false;
        for (int k = 0; k < rated.size(); k++)
        {
            if (rated[k] == animeId)
            {
                found = true;
                break;
            }
        }
        if (found)
        {
            num++; 
            continue;
        } 
        cout << db.getAnimeName(animeId) 
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
        else if (parts[0] == "showParams")
        {
            cout << "Num Factors " << model.numFactors << endl;
            cout << "Regularization Parameter " << model.regularize << endl;
            cout << "Gradient Tolerance " << model.gradTol << endl;
        }
        else if (parts[0] == "optRegularize")
        {
            if (parts.size() < 6)
            {
                cout << "Expected 5 arguments. See help\n";
                continue;
            }

            double ratio = atof(parts[1].c_str());
            int numTries = atoi(parts[2].c_str());

            double start = atof(parts[3].c_str());
            double end = atof(parts[4].c_str());
            double tol = atof(parts[5].c_str());
                
            double optRegularize = lineSearchRegularize(model, fullMatrix, 
                                                        ratio, numTries,
                                                        start, end, tol);
            model.setRegularizationParameter(optRegularize);

            cout << "Regularization Parameter set to " << optRegularize 
                 << endl; 
        }
        else if (parts[0] == "new")
        {
            model = LinearModel(3, 0.0);
        }
        else if (parts[0] == "load")
        {
            if (parts.size() < 2)
            {
                cout << "Expected 1 argument. See help\n";
                continue;
            }

            string filename = parts[1];
            ifstream inFile(filename.c_str());
            model.load(inFile);
            inFile.close(); 
        } 
        else if (parts[0] == "save")
        {
            if (parts.size() < 2)
            {
                cout << "Expected 1 argument. See help\n";
                continue;
            }

            string filename = parts[1];
            ofstream outFile(filename.c_str());
            model.save(outFile);
            outFile.close(); 
        } 
        else if (parts[0] == "help")
        {
            cout << "Commands Summary\n";
            cout << "quit\n"
                 << "\tquit the program\n\n";
            cout << "help\n"
                 << "\tprints this help statement\n\n";
            cout << "trainFull\n"
                 << "\ttrain on the full matrix\n\n";
            cout << "trainCross ratio num\n"
                 << "\trun cross validation test and print the test RMSE.\n"
                 << "\tDoes not modify the current model\n\n";
            cout << "recommend username num\n"
                 << "\tprint the highest recommended anime for some user\n\n";
            cout << "setRegularize p\n"
                 << "\tSet the regularization parameter\n\n";
            cout << "setNumFactors num\n"
                 << "\tSet the number of linear factors in each feature\n"
                 << "\tvector\n\n";
            cout << "setGradTol tol\n"
                 << "\tSet the gradient tolerance for stopping\n"
                 << "\tminimization\n\n";
            cout << "showParams\n" 
                 << "\tprint the values of the model parameters\n\n";
            cout << "optRegularize ratio num start end tol\n"
                 << "\tFinds the optimal regularization parameter by a line\n"
                 << "\tsearch\n\n";
            cout << "new\n"
                 << "\tResets the model to default parameters\n\n";
            cout << "load filename\n"
                 << "\tLoads the model from a file\n\n";
            cout << "save filename\n"
                 << "\tSaves the model to a file\n\n";
        }
        else
        {
            cout << "Unrecognized command. See help\n";
        }
    } 

    return 0;
}
