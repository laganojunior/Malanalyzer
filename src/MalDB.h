#ifndef __MAL_DB__
#define __MAL_DB__


// This module contains the database interfaces

#include <iostream>
#include <vector>
#include <map>
#include <sqlite3.h>

#include "Matrix.h"

using namespace std;

class MalDBReader 
{
    public :
    MalDBReader(string filename);
	~MalDBReader();

    int getUserId(const string& name);
    int getAnimeId(const string& name);

    unsigned int getNumUsers();
    unsigned int getNumAnime();
        
    string& getUserName(unsigned int userId);
    string& getAnimeName(unsigned int userId);

	const vector<double>& getAnimeRatings(unsigned int userId);
	const vector<double>& getUserRatings(unsigned int animeId);

	const vector<unsigned int>& getAnimeRated(unsigned int userId);
	const vector<unsigned int>& getUserRaters(unsigned int animeId);

    const vector<vector <double> > & getRatingsMatrix();
    const vector<vector <double> > & getRatingsMatrixTranspose();

    const vector<vector <unsigned int> >& getAnimeRatedList();
    const vector<vector <unsigned int> >& getUserRatersList();

    const Matrix& getMatrix();

    private:
    sqlite3 * dbConn;

    vector<string> usernames;
    vector<string> animenames;   
	
	vector<vector<unsigned int> > userToAnimeRated;
	vector<vector<double> > ratingsMatrix;

	vector<vector<unsigned int> > animeToUserRated;
	vector<vector<double> > ratingsMatrixTranspose;

    Matrix matrix;    
};

#endif
