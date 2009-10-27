import sqlite3
from Bimap import Bimap
import pysparse

class DBWriter:
    """
    This class provides an interface for adding entries into the database.
    Changes made are not saved until saveChanges() is called. 
    """
    
    def __init__(self, dbName):
        self.conn = sqlite3.connect(dbName)
        
    def addUser(self, username, id):
        self.conn.cursor().execute("insert or ignore into userIds('id','name') \
                                    values(?,?)", (id, username))
        
    def addAnime(self, animename, id):
        self.conn.cursor().execute("insert or ignore into \
                     animeIds('id','name') values(?,?)", (id, animename))
        
    def addAnimeRating(self, userId, animeId, rating):
        self.conn.cursor().execute("insert or replace into ratings('userId',\
               'animeId','rating') values(?,?,?)", (userId, animeId, rating))
        
    def saveChanges(self):
        self.conn.commit()
            
class MemReader:
    """
    A memory reader for the sqlite3 database. It reads data from the database 
    and stores a copy in memory, which can then be quickly accessed without 
    accessing the hard drive. This does mean that changes made afterward to the
    database are not viewable from the memory reader.

    Also, anime and users are typically referred to their index in the 
    list of animes and users, rather than the UID of the site. This makes
    it easier to construct the ratings matrix.
    """

    def __init__(self, dbName):
        conn = sqlite3.connect(dbName)
                
        # Read the anime ids and names 
        c = conn.cursor()
        c.execute("select id, name from animeIds")

        animeIdStrings = [(row[0], row[1]) for row in c]
        animeIdIndices = [(pair[0], i) for i, pair in\
                           enumerate(animeIdStrings)]
        animeStringMap = Bimap(animeIdStrings, enforceBijection = False)
        animeIndexMap = Bimap(animeIdIndices, enforceBijection = False)
        c.close()

        # Read the user ids and names
        c = conn.cursor()
        c.execute("select id, name from userIds")

        userIdStrings = [(row[0], row[1]) for row in c]
        userIdIndices = [(pair[0], i) for i, pair in\
                           enumerate(userIdStrings)]
        userStringMap = Bimap(userIdStrings, enforceBijection = False)
        userIndexMap = Bimap(userIdIndices, enforceBijection = False)
        c.close()

        # Read all ratings triples and feed them into the matrix
        c = conn.cursor()
        c.execute("select userId, animeId, rating from ratings where rating \
                   <> 0")

        self.ratingsMatrix = pysparse.spmatrix.ll_mat(len(userIdStrings),
                                                      len(animeIdStrings))
        for row in c:
            userId = row[0]
            animeId = row[1]
            rating = row[2]
            
            userIndex  = userIndexMap.value(userId)
            animeIndex = animeIndexMap.value(animeId)
            self.ratingsMatrix[userIndex, animeIndex] = rating
            
        c.close()

        # Now create a bimap between indices and names directly, so that
        # the ids are no longer needed.
        userIndexStrings = [(index, userStringMap.value(\
                                    userIndexMap.key(index)))\
                            for index in range(len(userIdStrings))]

        animeIndexStrings = [(index, animeStringMap.value(\
                              animeIndexMap.key(index)))\
                            for index in range(len(animeIdStrings))]

        self.userMap = Bimap(userIndexStrings, enforceBijection = False)
        self.animeMap = Bimap(animeIndexStrings, enforceBijection = False)
        self.numUsers = len(userIdStrings)
        self.numAnime = len(animeIdStrings)


    def getUserIndex(self, username):
        return self.userMap.key(username)
        
    def getAnimeIndex(self, animename):
        return self.animeMap.key(animename)
        
    def getNumUsers(self):
        return self.numUsers
        
    def getNumAnime(self):
        return self.numAnime

    def getUserName(self, userIndex):
        return self.userMap.value(userIndex)
        
    def getAnimeName(self, animeIndex):
        return self.animeMap.value(animeIndex)

    def getAnimeRatingsForUser(self, userIndex):
        userMat = self.ratingsMatrix[userIndex, :]
        
        nonZeroRatings = [(col, rating) for ((row, col), rating) in\
                          userMat.items()]
 
        return dict(nonZeroRatings) 


    def getUserRatingsForAnime(self, animeIndex):
        animeMat = self.ratingsMatrix[:, animeIndex]
        
        nonZeroRatings = [(row, rating) for ((row, col), rating) in\
                          animeMat.items()]

        return dict(nonZeroRatings)
 
    def getRatingsMatrix(self):
        return self.ratingsMatrix


    

    
            
        
            
            
        
