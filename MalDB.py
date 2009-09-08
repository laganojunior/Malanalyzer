import sqlite3
from CleanText import replaceUnicode, unescapeHtml

class MalDB:
    
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
            raise MalDBException("No id for username %s" % (username))
            
        return row[0]
        
    def getAnimeId(self, animename):
        c = self.conn.cursor()
        
        c.execute("select id from animeIds where name=?", (animename,))
        row = c.fetchone()
        
        if row is None:
            raise Exception("No id for anime %s" % (animename))
        
        return row[0]
        
    def addAnimeRating(self, userId, animeId, rating):
        self.conn.cursor().execute("insert or replace into ratings('userId','animeId','rating') values(?,?,?)", (userId, animeId, rating))
        
    def saveChanges(self):
        self.conn.commit()
        
    def addAnimeList(self, userid, animelist):
        # Go through each anime in the list
        for anime in animelist:
            # Clean up the anime's string to remove html escapes and unicode 
            # characters
            name = replaceUnicode(unescapeHtml(anime["title"]))
            
            # Add an id entry for the anime. Note that one is already provided
            # in the list
            id = anime["id"]
            self.addAnime(name, id)
            
            # Add an entry for the user's rating
            self.addAnimeRating(userid, id, anime["score"])
            
        
            
            
        