import WebGrab
import MalDB
from CleanText import replaceUnicode, unescapeHtml

def addAnimeList(db, userid, username, animelist):
    # Make sure the user has an id in the database
    db.addUser(username, userid)

    # Go through each anime in the list
    for anime in animelist:
        # Clean up the anime's string to remove html escapes and unicode 
        # characters
        name = replaceUnicode(unescapeHtml(anime["title"]))
        
        # Add an id entry for the anime. Note that one is already provided
        # in the list
        id = anime["id"]
        db.addAnime(name, id)
        
        # Add an entry for the user's rating
        db.addAnimeRating(userid, id, anime["score"])

def addUserData(username, db):
    """
    Adds a username and all of its ratings to a MalDB.
    
    Arguments:
    username - the username to add
    db       - the MalDB instance to add the data to
    """
    
    animelist = WebGrab.getAnimeList(username)
    userid = WebGrab.getUserId(username)

    addAnimeList(db, userid, username, animelist)
