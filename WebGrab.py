import urllib.request
import json
import re

def getAnimeList(username):
    apiUrl = "http://mal-api.com/animelist/" + username
    f = urllib.request.urlopen(apiUrl)
    j = json.loads(f.read().decode())
    return j["anime"]
    
def getUserId(username):
    profileUrl = "http://myanimelist.net/profile/" + username
    f = urllib.request.urlopen(profileUrl)
    
    profileHtml = f.read().decode()
    
    userIdRegEx = r'<a href="http://myanimelist.net/myfriends.php\?go=add&id=([0-9]+)" title=".*">Send Friend Request</a>'
    
    m = re.search(userIdRegEx, profileHtml)
    
    if m is None:
        raise Exception("No RegEx match in getUserId for %s" % username)
        
    return m.group(1)
       