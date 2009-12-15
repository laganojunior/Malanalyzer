#include "MalDB.h"
#include <sqlite3.h>
#include <stdlib.h>
#include <assert.h>
#include <cstdlib>

MalDBReader :: MalDBReader(string filename)
{
    sqlite3_open(filename.c_str(), &dbConn);

    int numRows;
    int numCols;
    char * errorString;
    char ** results;
    string query;

	map<unsigned int, unsigned int> userIdToIndex;
	map<unsigned int, unsigned int> animeIdToIndex;

	// Load up user ids
    query = string("select id, name from userIds");

    sqlite3_get_table(dbConn, query.c_str(), &results, &numRows,
                                &numCols, &errorString);

    for (int i = 1; i <= numRows; i++) 
    {
        unsigned int id = atoi(results[i * numCols]);
        string name = string(results[i * numCols + 1]);

        usernames.push_back(name);
		userIdToIndex.insert(pair<unsigned int, unsigned int>(id, i -1));
    }

	sqlite3_free_table(results);


	// Load up anime ids

    query = string("select id, name from animeIds");

    sqlite3_get_table(dbConn, query.c_str(), &results, &numRows,
                                &numCols, &errorString);

    for (int i = 1; i <= numRows; i++) 
    {
        unsigned int id = atoi(results[i * numCols]);
        string name = string(results[i * numCols + 1]);

        animenames.push_back(name);
		animeIdToIndex.insert(pair<unsigned int, unsigned int>(id, i -1));
    }

	sqlite3_free_table(results);

	// Load up ratings

	userToAnimeRated.resize(usernames.size());
	ratingsMatrix.resize(usernames.size());

	animeToUserRated.resize(animenames.size());
	ratingsMatrixTranspose.resize(animenames.size());
	
	query = string("select userid, animeid, rating from ratings where rating <> 0");

    sqlite3_get_table(dbConn, query.c_str(), &results, &numRows,
                                &numCols, &errorString);

    for (int i = 1; i <= numRows; i++) 
    {
        unsigned int user  = atoi(results[i * numCols]);
		unsigned int anime = atoi(results[i * numCols + 1]);
        double rating = strtod(results[i * numCols + 2], NULL);

		unsigned int userIndex  = userIdToIndex.find(user)  -> second;
		unsigned int animeIndex = animeIdToIndex.find(anime) -> second;

        userToAnimeRated[userIndex].push_back(animeIndex);
		ratingsMatrix[userIndex].push_back(rating);

        animeToUserRated[animeIndex].push_back(userIndex);
		ratingsMatrixTranspose[animeIndex].push_back(rating);

    }

	sqlite3_free_table(results);
	
}

MalDBReader :: ~MalDBReader()
{
	sqlite3_close(dbConn);

}


unsigned int MalDBReader :: getUserId(const string& name)
{
	int index = 0;
	for (; usernames[index] != name && index < usernames.size(); index++);

	assert(index <= usernames.size());
	
	return index;
}

unsigned int MalDBReader :: getAnimeId(const string& name)
{
	int index = 0;
	for (; animenames[index] != name && index < animenames.size(); index++);

	assert(index <= animenames.size());
	
	return index;
}

unsigned int MalDBReader :: getNumUsers()
{
	return usernames.size();
}

unsigned int MalDBReader :: getAnimeUsers()
{
	return animenames.size();
}

        
string& MalDBReader :: getUserName(unsigned int userId)
{
	return usernames[userId];
}
        
string& MalDBReader :: getAnimeName(unsigned int animeId)
{
    return animenames[animeId];
}

const vector<double>& MalDBReader :: getAnimeRatings(unsigned int userId)
{
	return ratingsMatrix[userId];
}

const vector<double>& MalDBReader :: getUserRatings(unsigned int animeId)
{
	return ratingsMatrixTranspose[animeId];
}

const vector<unsigned int>& MalDBReader :: getAnimeRated(unsigned int userId)
{
	return userToAnimeRated[userId];
}

const vector<unsigned int>& MalDBReader :: getUserRaters(unsigned int animeId)
{
	return animeToUserRated[animeId];
}

const vector< vector<double> >& MalDBReader :: getRatingsMatrix()
{
    return ratingsMatrix;
}

const vector< vector<double> >& MalDBReader :: getRatingsMatrixTranspose()
{
    return ratingsMatrixTranspose;
}

const vector<vector <unsigned int> >& MalDBReader :: getAnimeRatedList()
{
    return userToAnimeRated;
}

const vector<vector <unsigned int> >& MalDBReader :: getUserRatersList()
{
    return animeToUserRated;
}
