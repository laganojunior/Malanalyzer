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
    
def getRandomUsername():
    # Use the url for getting a random list
    url = "http://myanimelist.net/users.php?lucky=1"
    f = urllib.request.urlopen(url)

    # Extract the username from the title
    usernameRegex = r"<title>([\S]+)'s Anime List - MyAnimeList.net</title>"
    match = re.search(usernameRegex, f.read().decode())

    if match is None:
        raise Exception("No regular expression match")
        
    return match.group(1)
       