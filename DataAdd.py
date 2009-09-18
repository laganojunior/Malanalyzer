import WebGrab
import MalDB

def addUserData(username, db):
    """
    Adds a username and all of its ratings to a MalDB.
    
    Arguments:
    username - the username to add
    db       - the MalDB instance to add the data to
    """
    
    animelist = WebGrab.getAnimeList(username)
    userid = WebGrab.getUserId(username)

    db.addUser(username, userid)
    db.addAnimeList(userid, animelist)