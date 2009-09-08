from MalDB import MalDB
from CleanText import replaceUnicode, unescapeHtml
import WebGrab

db = MalDB("Mal.db")

username = "lelouch9178"
   
animelist = WebGrab.getAnimeList(username)
userid = WebGrab.getUserId(username)

db.addUser(username, userid)
db.addAnimeList(userid, animelist)
db.saveChanges()


