import sqlite3
from Bimap import Bimap

class MalDB:
    """
    This is the interface to the underlying sqlite3 database stored on the hard
    disk. All I/O functions will apply directly to the database connection, so
    changes outside of this connection are immediately visible. For changes made
    in this connection to be viewable outside, call saveChanges()
    """
    
    def __init__(self, dbName):
        self.conn = sqlite3.connect(dbName)
        
    def addUser(self, username, id):
        self.conn.cursor().execute("insert or ignore into userIds('id','name') values(?,?)", (id, username))
        
    def addAnime(self, animename, id):
        self.conn.cursor().execute("insert or ignore into animeIds('id','name') values(?,?)", (id, animename))
        
    def getUserId(self, username):
        c = self.conn.cursor()
        
        c.execute("select id from userIds where name=?", (username,))
        row = c.fetchone()
        
        if row is None:
            raise Exception("No id for username %s" % (username))
            
        return row[0]
        
    def getAnimeId(self, animename):
        c = self.conn.cursor()
        
        c.execute("select id from animeIds where name=?", (animename,))
        row = c.fetchone()
        
        if row is None:
            raise Exception("No id for anime %s" % (animename))
        
        return row[0]
        
    def getAllUserIds(self):
        c = self.conn.cursor()
        
        c.execute("select distinct id from userIds")
        
        return [row[0] for row in c]
        
    def getAllAnimeIds(self):
        c = self.conn.cursor()
        
        c.execute("select distinct id from animeIds")
        
        return [row[0] for row in c]
        
    def getUserName(self, userId):
        c = self.conn.cursor()
        
        c.execute("select name from userIds where id=?", (userId,))
        row = c.fetchone()
        
        if row is None:
            raise Exception("No username for id %s" % (userId))
            
        return row[0]
        
    def getAnimeName(self, animeId):
        c = self.conn.cursor()
        
        c.execute("select name from animeIds where id=?", (animeId,))
        row = c.fetchone()
        
        if row is None:
            raise Exception("No anime name for id %s" % (animeId))
            
        return row[0]
        
    def addAnimeRating(self, userId, animeId, rating):
        self.conn.cursor().execute("insert or replace into ratings('userId','animeId','rating') values(?,?,?)", (userId, animeId, rating))
        
    def saveChanges(self):
        self.conn.commit()
            
    def getAnimeRatingsForUser(self, userId):
        """
        Returns a dictionary mapping animeIds to ratings for a particular user
        
        Arguments:
        userId - the id of the user to getting anime ratings for
        """
        
        c = self.conn.cursor()
        c.execute("select animeId, rating from ratings where userId=? and rating <> 0", (userId,))
        
        ratingMap = {}
        
        for row in c:
            ratingMap[row[0]] = row[1]
            
        return ratingMap
        
    def getUserRatingsForAnime(self, animeId):
        """
        Returns a dictionary mapping userIds to ratings for a particular anime
        
        Arguments:
        animeId - the id of the anime to getting user ratings for
        """
        
        c = self.conn.cursor()
        c.execute("select userId, rating from ratings where animeId=? and rating <> 0", (animeId,))
        
        ratingMap = {}
        
        for row in c:
            ratingMap[row[0]] = row[1]
            
        return ratingMap
        
    def getRatingsMatrix(self):
        """
        Returns a multi-dimensional dictionary mapping a user and anime to the
        respective rating
        """
        
        c = self.conn.cursor()
        c.execute("select userId, animeId, rating from ratings where rating <> 0")
        
        ratingMap = {}
        
        for row in c:
            userId = row[0]
            animeId = row[1]
            rating = row[2]
            
            if userId not in ratingMap:
                ratingMap[userId] = {}

            ratingMap[userId][animeId] = rating

        return ratingMap

class MemReader:
    """
    A memory reader for the sqlite3 database. It reads data from the database 
    and stores a copy in memory, which can then be quickly accessed without 
    accessing the hard drive. This does mean that changes made afterward to the
    database are not viewable from the memory reader, so this should only be 
    used when several accesses on a snapshot of the database is required. 
    The reader supports all non-write operations of MalDB.
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
        c.execute("select userId, animeId, rating from ratings where rating <> 0")

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


    

    
            
        
            
            
        
