import sqlite3
from Bimap import Bimap

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
                
        # Read the anime id bimap
        c = conn.cursor()
        c.execute("select id, name from animeIds")

        animeIdPairs = [(row[0], row[1]) for row in c]
        self.animeIdMap = Bimap(animeIdPairs, enforceBijection = False)
        self.animeIds = [pair[0] for pair in animeIdPairs]
        c.close()

        # Read the user id bimap
        c = conn.cursor()
        c.execute("select id, name from userIds")

        userIdPairs = [(row[0], row[1]) for row in c]
        self.userIdMap = Bimap(userIdPairs, enforceBijection = False)
        self.userIds = [pair[0] for pair in userIdPairs]
        c.close()

        # Read all ratings triples
        c = conn.cursor()
        c.execute("select userId, animeId, rating from ratings where rating \
                   <> 0")

        ratingTriples = [(row[0], row[1], row[2]) for row in c]
        c.close()

        # Convert the ratings triples to the desired mappings
        self.userRatingMap = {}
        self.animeRatingMap = {}

        for (userId, animeId, rating) in ratingTriples:
            if userId not in self.userRatingMap:
                self.userRatingMap[userId] = {}

            self.userRatingMap[userId][animeId] = rating

            if animeId not in self.animeRatingMap:
                self.animeRatingMap[animeId] = {}
            
            self.animeRatingMap[animeId][userId] = rating

    def getUserId(self, username):
        return self.userIdMap.key(username)
        
    def getAnimeId(self, animename):
        return self.animeIdMap.key(animename)
        
    def getAllUserIds(self):
        return self.userIds
        
    def getAllAnimeIds(self):
        return self.animeIds

    def getUserName(self, userId):
        return self.userIdMap.value(userId)
        
    def getAnimeName(self, animeId):
        return self.animeIdMap.value(animeId)

    def getAnimeRatingsForUser(self, userId):
        if userId not in self.userRatingMap:
            return {}

        return self.userRatingMap[userId]
        
    def getUserRatingsForAnime(self, animeId):
        if animeId not in self.animeRatingMap:
            return {}

        return self.animeRatingMap[animeId]
        
    def getRatingsMatrix(self):
        return self.userRatingMap


    

    
            
        
            
            
        
