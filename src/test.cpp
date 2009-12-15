#include "MalDB.h"
#include <assert.h>
#include "AveragePredictionModel.h"

int main() 
{
    MalDBReader db(string("Mal.db"));

	string username = "laganojunior";
	
	cout << "Username is: " << db.getUserName(db.getUserId(username)) << endl;

	string animename = "Cowboy Bebop";
	
	cout << "Name is: " << db.getAnimeName(db.getAnimeId(animename)) << endl;

	
	unsigned int userId = db.getUserId(username);

	const vector<unsigned int>& rated = db.getAnimeRated(userId);
	const vector<double>& ratings = db.getAnimeRatings(userId);

	assert(rated.size() == ratings.size());

	for (int i = 0; i < rated.size(); i++)
	{
		cout << db.getAnimeName(rated[i]) << " " << ratings[i] << endl;
	}

    AveragePredictionModel model;

    model.train(db.getRatingsMatrix(), db.getRatingsMatrixTranspose(),
                db.getAnimeRatedList(), db.getUserRatersList());
    
    cout << "RMSE is " << model.RMSE(db.getRatingsMatrix(),
                                     db.getRatingsMatrixTranspose(),
                                     db.getAnimeRatedList(),
                                     db.getUserRatersList()) << endl;

	cout << "hello" << endl;
    return 0;
}
